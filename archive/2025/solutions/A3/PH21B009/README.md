[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/irjfaQnA)

`fast_api_backend.py` has the fast API backed
  - It loads the model
  - fetched the JSON serialized bytes images
  - processes that image and predicts the written digit
  - returns the output in JSONSchema

`frontend_UI_app.py` has the frontend part
  - uses requests library to send the image and get the prediction
  - then sends outputs the prediction to the user via messagebox

How to run:
  - just download the repo
  - run the fast_api_backend.py file
  - then run the frontend_UI_app.py file

To run with docker container: (For windows)
  - open in the same folder
  - run this command "docker compose build" (without quotes)
  - then run this command "docker run fastapi_backend_app"
  - this will make your fast API backend, run in the docker container
