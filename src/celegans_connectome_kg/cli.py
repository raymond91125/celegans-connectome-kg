"""Command-line entry point for the pipeline.

Stages are stubs in Phase 0; each is filled in over the roadmap (see docs/PLANNING.md).
"""

from collections import Counter
from pathlib import Path

import click

DEFAULT_NEURON_GRAPH_DIR = Path("data/neuron-graph")


@click.group()
@click.version_option()
def main() -> None:
    """cckg — C. elegans connectome knowledge graph pipeline."""


@main.command()
@click.option(
    "--data-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=DEFAULT_NEURON_GRAPH_DIR,
    show_default=True,
    help="Pinned neuron-graph snapshot directory.",
)
def ingest(data_dir: Path) -> None:
    """Read pinned neuron-graph files into normalized records. [Phase 2]"""
    from celegans_connectome_kg.ingest.neuron_graph import load_neuron_graph

    data = load_neuron_graph(data_dir)
    by_type = Counter(c.connection_type for c in data.connections)
    by_dataset = Counter(c.dataset_id for c in data.connections)
    click.echo(f"cells:       {len(data.cells)}")
    click.echo(f"datasets:    {len(data.datasets)}")
    click.echo(f"connections: {len(data.connections)}")
    for t in ("chemical", "gap_junction", "functional"):
        click.echo(f"  {t:13} {by_type.get(t, 0)}")
    click.echo(f"datasets with connections: {len(by_dataset)}")


@main.command()
def match() -> None:
    """Resolve cell names to WBbt anatomy URIs; emit the match report. [Phase 2]"""
    raise click.ClickException("not yet implemented (Phase 2)")


@main.command()
def build() -> None:
    """Assemble LinkML data (cells, connections, datasets, evidence). [Phase 3]"""
    raise click.ClickException("not yet implemented (Phase 3)")


@main.command()
def export() -> None:
    """Serialize RDF/OWL and the neuron-graph JSON projection. [Phase 3]"""
    raise click.ClickException("not yet implemented (Phase 3)")


if __name__ == "__main__":
    main()
