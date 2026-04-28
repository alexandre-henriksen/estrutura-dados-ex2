import os
import time
import sys
from merge_sort import merge_sort
from quick_sort import quick_sort

# ──────────────────────────────────────────────
# Configurações
# ──────────────────────────────────────────────
INSTANCES_DIR = r"C:\Users\USER\Documents\notebooks\estrutura_dados_ex2\instancias-num"
OUTPUT_DIR = r"C:\Users\USER\Documents\notebooks\estrutura_dados_ex2\output"
RESULTS_DIR = r"C:\Users\USER\Documents\notebooks\estrutura_dados_ex2\results"
ALGORITHMS = {
    "Merge Sort": merge_sort,
    "Quick Sort": quick_sort,
}
CLASSES = [1000, 10000, 100000]


# ──────────────────────────────────────────────
# Utilitários
# ──────────────────────────────────────────────
def load_instance(filepath):
    """Lê um arquivo de instância e retorna uma lista de inteiros."""
    with open(filepath, "r") as f:
        return [int(line.strip()) for line in f if line.strip()]


def format_time(seconds):
    """Formata segundos para exibição legível."""
    if seconds < 1e-3:
        return f"{seconds * 1e6:.2f} µs"
    if seconds < 1:
        return f"{seconds * 1e3:.2f} ms"
    return f"{seconds:.4f} s"


def separator(char="-", width=72):
    print(char * width)


# ──────────────────────────────────────────────
# Coleta de instâncias
# ──────────────────────────────────────────────
def collect_instances(directory):
    """
    Agrupa arquivos .in por classe (tamanho) e os ordena.
    Retorna dict: {1000: [...], 10000: [...], 100000: [...]}
    """
    groups = {c: [] for c in CLASSES}

    if not os.path.isdir(directory):
        print(f"[ERRO] Pasta '{directory}' não encontrada.")
        sys.exit(1)

    for filename in sorted(os.listdir(directory)):
        if not filename.endswith(".in"):
            continue
        # Espera formato: num.<tamanho>.<variante>.in
        parts = filename.split(".")
        if len(parts) < 3:
            continue
        try:
            size = int(parts[1])
        except ValueError:
            continue
        if size in groups:
            groups[size].append(os.path.join(directory, filename))

    return groups


# ──────────────────────────────────────────────
# Benchmark
# ──────────────────────────────────────────────
def benchmark(groups):
    """
    Executa cada algoritmo em cada instância.
    Retorna:
      results[algo][size] = [tempo1, tempo2, ...]
    """
    results = {algo: {c: [] for c in CLASSES} for algo in ALGORITHMS}

    for size in CLASSES:
        files = groups[size]
        if not files:
            print(f"\n[AVISO] Nenhuma instância encontrada para tamanho {size}.")
            continue

        separator("=")
        print(f"  Classe: {size} entradas  ({len(files)} instância(s))")
        separator("=")

        for filepath in files:
            filename = os.path.basename(filepath)
            print(f"\n  Arquivo: {filename}")
            separator()

            data_original = load_instance(filepath)

            for algo_name, algo_fn in ALGORITHMS.items():
                data = data_original.copy()          # preserva original
                start = time.perf_counter()
                algo_fn(data)
                elapsed = time.perf_counter() - start

                results[algo_name][size].append(elapsed)
                print(f"    {algo_name:<20} → {format_time(elapsed)}")

                # importante: salva o resultado ordenado na pasta output
                algo_slug = algo_name.lower().replace(" ", "_")
                out_name = filename.replace(".in", f".{algo_slug}.out")
                out_path = os.path.join(OUTPUT_DIR, out_name)
                with open(out_path, "w") as f:
                    f.write("\n".join(str(x) for x in data))


    return results


# ──────────────────────────────────────────────
# Exibição dos resultados
# ──────────────────────────────────────────────
def print_summary(results):
    """Imprime a média por algoritmo (geral) e a tabela por classe."""

    separator("=")
    print("  MÉDIAS POR ALGORITMO (todas as instâncias)")
    separator("=")
    for algo_name in ALGORITHMS:
        all_times = []
        for times in results[algo_name].values():
            all_times.extend(times)
        if all_times:
            avg = sum(all_times) / len(all_times)
            print(f"    {algo_name:<20} → {format_time(avg)}")
        else:
            print(f"    {algo_name:<20} → sem dados")

    print()
    separator("=")
    print("  TABELA: MÉDIA POR CLASSE E ALGORITMO")
    separator("=")

    # Cabeçalho
    col_w = 14
    header = f"  {'Algoritmo':<22}"
    for c in CLASSES:
        label = f"{c} ent."
        header += f"{label:>{col_w}}"
    print(header)
    separator()

    # Linhas
    for algo_name in ALGORITHMS:
        row = f"  {algo_name:<22}"
        for c in CLASSES:
            times = results[algo_name][c]
            if times:
                avg = sum(times) / len(times)
                row += f"{format_time(avg):>{col_w}}"
            else:
                row += f"{'N/A':>{col_w}}"
        print(row)

    separator("=")

# Summarurização para Markdown
def get_summary_text(results):
    lines = []

    lines.append("# Resultados do Benchmark\n")

    lines.append("## Médias por Algoritmo\n")
    for algo_name in ALGORITHMS:
        all_times = []
        for times in results[algo_name].values():
            all_times.extend(times)
        if all_times:
            avg = sum(all_times) / len(all_times)
            lines.append(f"- {algo_name}: {format_time(avg)}")
        else:
            lines.append(f"- {algo_name}: sem dados")

    lines.append("\n## Tabela por Classe\n")

    header = "| Algoritmo | " + " | ".join(f"{c}" for c in CLASSES) + " |"
    sep = "|" + "---|" * (len(CLASSES) + 1)

    lines.append(header)
    lines.append(sep)

    for algo_name in ALGORITHMS:
        row = [algo_name]
        for c in CLASSES:
            times = results[algo_name][c]
            if times:
                avg = sum(times) / len(times)
                row.append(format_time(avg))
            else:
                row.append("N/A")
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)

# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────
def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else INSTANCES_DIR

    print()
    separator("=")
    print(f"  Benchmark de Ordenação por Comparação")
    print(f"  Pasta de instâncias: {directory}")
    separator("=")

    groups = collect_instances(directory)
    results = benchmark(groups)

    print()
    print_summary(results)
    print()

    summary_text = get_summary_text(results)
    results_path = os.path.join(RESULTS_DIR, "results.md")
    with open(results_path, "w") as f:
        f.write(summary_text)

if __name__ == "__main__":
    main()
