from invoke import task
import sys
import os
import pathlib
def clear_logs():
    with open(os.path.join(pathlib.Path.cwd(), "logs", "main.log"), 'w') as log:
        log.write("")

@task(default=True)
def start(ctx, port=7500):
    try:
        os.environ["GRADIO_SERVER_PORT"] = str(port)
        os.environ["GRADIO_NUM_PORTS"] = str(1000)
        os.environ["GRADIO_NODE_NUM_PORTS"] = str(1000)
        os.environ["GRADIO_ANALYTICS_ENABLED"] = "True"
        print(f"Starting Generator Server on port {port}...")    
        ctx.run(f'{os.getenv("PYTHONPATH")} app.py', pty=True)
    except KeyboardInterrupt:
        print("Shutting Down Server... Clearing Logs... ")
        clear_logs()
        sys.exit(0)
        print("Server Shut Down")

def test(ctx):
    ctx.run("python -m pytest ")
