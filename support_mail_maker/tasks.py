from invoke import task

@task(default=True)
def start(ctx):
    ctx.run("python app.py.")

def test(ctx):
    ctx.run("python -m pytest ")