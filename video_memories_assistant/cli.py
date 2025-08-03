import typer

app = typer.Typer()

@app.command()
def extract(input: str):
    """Extract metadata and frames"""
    print(f"Extracting from {input}...")

@app.command()
def sync_audio(input: str):
    """Synchronize external audio tracks"""
    print(f"Syncing audio in {input}...")

