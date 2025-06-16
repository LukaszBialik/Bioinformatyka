from copy import deepcopy
import xml.etree.ElementTree as ET
import Sequencer
import AntColonySequencer
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os


def load_probes_from_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    length = int(root.attrib['length'])
    start = root.attrib['start']

    probes = root.findall('probe')
    S1 = []
    S2 = []

    if len(probes) == 2:
        S1 = [cell.text.strip() for cell in probes[0].findall('cell')]
        S2 = [cell.text.strip() for cell in probes[1].findall('cell')]
    else:
        raise ValueError("Expected two probes in the XML")

    return S1, S2, length, start

def build_combined_spectrum(S1, S2):
    combined_spectrum = []
    for c1 in S1:
        prefix1 = c1[:-2]
        for c2 in S2:
            prefix2 = c2[:-1]
            if prefix1 == prefix2:
                new_oligo = prefix1 + c2[-1] + c1[-1]
                combined_spectrum.append(new_oligo)
    sqpe = len(S1) + len(S2) - 2*len(combined_spectrum)
    return combined_spectrum, sqpe

def main(inputDir = 'K'):
    for i in range(5):  # Test for input0.xml to input5.xml
        xml_file = f'{inputDir}/input{i}.xml'
        print(f"\n--- Testing {xml_file} ---")

        S1, S2, length, start = load_probes_from_xml(xml_file)
        sequencer = Sequencer.Sequencer(S1, S2, length, start)
        result_sequence, sqpe, time, usedOligos = sequencer.run()
        print(f"[Greedy] Finished in {time}s, used {usedOligos} oligos ({sqpe - 3} positive errors).")
        print(result_sequence)

        spectrum, sqpeInit = build_combined_spectrum(S1, S2)
        aco = AntColonySequencer.AntColonySequencer(spectrum, target_length=length, start_seq=start)
        best_seq, best_path, time, usedOligos, sqpe, iteration, ant = aco.run(n_ants=10, n_iterations=100)
        print(f"[ACO] Finished in {time}s, used {usedOligos} oligos ({sqpe - 3} positive errors), best from iteration {iteration+1}, ant {ant+1}.")
        print(best_seq)
    
    
def collect_times(inputDir = 'K'):
    results = {
        'k': [],
        'algorithm': [],
        'time_ms': []
    }
    howManyFiles = 0
    if (inputDir == 'K'): 
        howManyFiles = 5
    else:
        howManyFiles = 6
    for i in range(howManyFiles):  # input5.xml to input9.xml -> k = 6 to 10
        if (howManyFiles == 5): 
            k = i+6
        else:
            k = i*5
        xml_file = f'{inputDir}/input{i}.xml'
        print(f"Processing {xml_file}...")

        S1, S2, length, start = load_probes_from_xml(xml_file)

        # Greedy
        sequencer = Sequencer.Sequencer(S1, S2, length, start)
        _, _, time_greedy, _ = sequencer.run()
        results['k'].append(k)
        results['algorithm'].append('Greedy')
        results['time_ms'].append(time_greedy * 1000)  # convert to ms

        # ACO
        spectrum, _ = build_combined_spectrum(S1, S2)
        aco = AntColonySequencer.AntColonySequencer(spectrum, target_length=length, start_seq=start)
        _, _, time_aco, _, _, _, _ = aco.run(n_ants=10, n_iterations=100)
        results['k'].append(k)
        results['algorithm'].append('ACO')
        results['time_ms'].append(time_aco * 1000)

    return pd.DataFrame(results)

def plot_execution_times(df, inputDir = 'K'):
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='k', y='time_ms', hue='algorithm', marker='o')
    plt.title("Czas działania algorytmów względem parametru k")
    if (inputDir == 'K'): 
        plt.xlabel("Parametr k")
    else:
        plt.xlabel("Liczba błędów pozytywnych [%]")
    plt.ylabel("Czas [ms]")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    df_times = collect_times('PE') 
    plot_execution_times(df_times, 'PE') #Rysowanie wykresów
    # main('K') # Pokazywanie rozwiązań
    
        # Należy wybrać jaki parametr chcemy badać 'K'-parametr k, 'PE'-ilość błędów poz. Domyślnie 'K'