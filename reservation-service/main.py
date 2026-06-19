from reservation_app import create_app

app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # noqa: Bind to all interfaces required for Docker
