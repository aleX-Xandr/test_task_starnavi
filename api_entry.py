import uvicorn

from app.containers import container
from app.logger import setup_logging
from app.utils import setup_app

setup_logging()
app = setup_app()


if __name__ == "__main__":
    # run main loop of application

    config = container.config()

    uvicorn.run(
        "api_entry:app",
        host="0.0.0.0",
        port=config.env.port,
        debug=config.env.debug,
        reload=config.env.debug,
        proxy_headers=True,
        log_config=None,
    )
