import xml.etree.ElementTree as ET
from pythonProject.bio import Sequencer
import AntColonySequencer


def load_probes_from_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    length = int(root.attrib['length'])
    start = root.attrib['start']

    probes = root.findall('probe')

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
    sqpe = len(S1) + len(S2) - 2 * len(combined_spectrum)
    return combined_spectrum, sqpe


def main():
    xml_file = 'input1.xml'
    S1, S2, length, start = load_probes_from_xml(xml_file)
    sequencer = Sequencer.Sequencer(S1, S2, length, start)
    result_sequence, sqpe, time, usedOligos = sequencer.run()
    print(f"Exact algorithm finished in {time}, used {usedOligos} oligos({sqpe - 3} positive errors). Final sequence is:")
    print(result_sequence)

    spectrum, sqpeInit = build_combined_spectrum(S1, S2)
    aco = AntColonySequencer.AntColonySequencer(spectrum, target_length=length, start_seq=start)
    best_seq, best_path, time, usedOligos, sqpe, iteration, ant = aco.run(n_ants=10, n_iterations=100)
    print(f"Heuristic algorithm finished in {time}. Final sequence is:")
    print(best_seq)


if __name__ == "__main__":
    main()
