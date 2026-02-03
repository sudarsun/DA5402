FROM debian:bookworm-slim
LABEL org.opencontainers.image.authors="sudarsun@dsai.iitm.ac.in"
RUN apt-get -y update
RUN apt-get -y install cowsay
RUN apt-get clean
COPY whale.cow /usr/share/cowsay/cows/whale.cow
ENTRYPOINT ["/usr/games/cowthink", "-f", "whale"]
