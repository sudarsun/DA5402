from ray.train import RunConfig, ScalingConfig
from ray.train.torch import TorchTrainer
import ray
import ray.train
import ray.train.torch

import tempfile
import uuid
import os
from typing import Dict

import torch
from filelock import FileLock
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.transforms import Normalize, ToTensor
from torchvision.models import VisionTransformer
from tqdm import tqdm

os.makedirs("/tmp/cluster_storage", exist_ok=True)

def get_dataloaders(batch_size):
    # Transform to normalize the input images.
    transform = transforms.Compose([ToTensor(), Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

    with FileLock(os.path.expanduser("~/data.lock")):
        # Download training data from open datasets.
        training_data = datasets.CIFAR10(
            root="~/data",
            train=True,
            download=True,
            transform=transform,
        )

        # Download test data from open datasets.
        testing_data = datasets.CIFAR10(
            root="~/data",
            train=False,
            download=True,
            transform=transform,
        )

    # Create data loaders.
    train_dataloader = DataLoader(training_data, batch_size=batch_size, shuffle=True)
    test_dataloader = DataLoader(testing_data, batch_size=batch_size)

    return train_dataloader, test_dataloader

@ray.remote(num_gpus=0.5)
def train_func():
    lr = 1e-3
    epochs = 1
    batch_size = 64 #512

    # Get data loaders inside the worker training function.
    train_dataloader, valid_dataloader = get_dataloaders(batch_size=batch_size)

    model = VisionTransformer(
        image_size=32,   # CIFAR-10 image size is 32x32
        patch_size=4,    # Patch size is 4x4
        num_layers=12,   # Number of transformer layers (12)
        num_heads=8,     # Number of attention heads (8)
        hidden_dim=128,  # Hidden size (can be adjusted) (384)
        mlp_dim=256,     # MLP dimension (can be adjusted) (768)
        num_classes=10   # CIFAR-10 has 10 classes
    )
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)

    # Model training loop.
    for epoch in range(epochs):
        model.train()
        for X, y in tqdm(train_dataloader, desc=f"Train Epoch {epoch}"):
            X, y = X.to(device), y.to(device)
            pred = model(X)
            loss = loss_fn(pred, y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        model.eval()
        valid_loss, num_correct, num_total = 0, 0, 0
        with torch.no_grad():
            for X, y in tqdm(valid_dataloader, desc=f"Valid Epoch {epoch}"):
                X, y = X.to(device), y.to(device)
                pred = model(X)
                loss = loss_fn(pred, y)

                valid_loss += loss.item()
                num_total += y.shape[0]
                num_correct += (pred.argmax(1) == y).sum().item()

        valid_loss /= len(train_dataloader)
        accuracy = num_correct / num_total

        print({"epoch_num": epoch, "loss": valid_loss, "accuracy": accuracy})

def train_func_per_worker(config: Dict):
    lr = config["lr"]
    epochs = config["epochs"]
    batch_size = config["batch_size_per_worker"]

    # Get data loaders inside the worker training function.
    train_dataloader, valid_dataloader = get_dataloaders(batch_size=batch_size)

    # [1] Prepare data loader for distributed training.
    # The prepare_data_loader method assigns unique rows of data to each worker so that
    # the model sees each row once per epoch.
    # NOTE: This approach only works for map-style datasets. For a general distributed
    # preprocessing and sharding solution, see the next part using Ray Data for data 
    # ingestion.
    # =================================================================================
    train_dataloader = ray.train.torch.prepare_data_loader(train_dataloader)
    valid_dataloader = ray.train.torch.prepare_data_loader(valid_dataloader)

    model = VisionTransformer(
        image_size=32,   # CIFAR-10 image size is 32x32
        patch_size=4,    # Patch size is 4x4
        num_layers=12,   # Number of transformer layers
        num_heads=8,     # Number of attention heads
        hidden_dim=128,  # Hidden size (can be adjusted)
        mlp_dim=256,     # MLP dimension (can be adjusted)
        num_classes=10   # CIFAR-10 has 10 classes
    )

    # [2] Prepare and wrap your model with DistributedDataParallel.
    # The prepare_model method moves the model to the correct GPU/CPU device.
    # =======================================================================
    model = ray.train.torch.prepare_model(model)

    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)

    # Model training loop.
    for epoch in range(epochs):
        if ray.train.get_context().get_world_size() > 1:
            # Required for the distributed sampler to shuffle properly across epochs.
            train_dataloader.sampler.set_epoch(epoch)

        model.train()
        for X, y in tqdm(train_dataloader, desc=f"Train Epoch {epoch}"):
            pred = model(X)
            loss = loss_fn(pred, y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        model.eval()
        valid_loss, num_correct, num_total = 0, 0, 0
        with torch.no_grad():
            for X, y in tqdm(valid_dataloader, desc=f"Valid Epoch {epoch}"):
                pred = model(X)
                loss = loss_fn(pred, y)

                valid_loss += loss.item()
                num_total += y.shape[0]
                num_correct += (pred.argmax(1) == y).sum().item()

        valid_loss /= len(train_dataloader)
        accuracy = num_correct / num_total

        # [3] (Optional) Report checkpoints and attached metrics to Ray Train.
        # ====================================================================
        with tempfile.TemporaryDirectory() as temp_checkpoint_dir:
            torch.save(
                model.module.state_dict(),
                os.path.join(temp_checkpoint_dir, "model.pt")
            )
            ray.train.report(
                metrics={"loss": valid_loss, "accuracy": accuracy},
                checkpoint=ray.train.Checkpoint.from_directory(temp_checkpoint_dir),
            )
            if ray.train.get_context().get_world_rank() == 0:
                print({"epoch_num": epoch, "loss": valid_loss, "accuracy": accuracy})

def train_cifar_10(num_workers, use_gpu):
    global_batch_size = 512

    train_config = {
        "lr": 1e-3,
        "epochs": 1,
        "batch_size_per_worker": global_batch_size // num_workers,
    }

    # [1] Start distributed training.
    # Define computation resources for workers.
    # Run `train_func_per_worker` on those workers.
    # =============================================
    scaling_config = ScalingConfig(num_workers=num_workers, use_gpu=use_gpu, resources_per_worker={"CPU": 4}) # "GPU": 1, 
    run_config = RunConfig(
        # /mnt/cluster_storage is an Anyscale-specific storage path.
        # OSS users should set up this path themselves.
        storage_path="/tmp/cluster_storage", 
        name=f"train_run-{uuid.uuid4().hex}",
    )
    trainer = TorchTrainer(
        train_loop_per_worker=train_func_per_worker,
        train_loop_config=train_config,
        scaling_config=scaling_config,
        run_config=run_config,
    )
    result = trainer.fit()
    print(f"Training result: {result}")

if __name__ == "__main__":
    train_cifar_10(num_workers=4, use_gpu=False)