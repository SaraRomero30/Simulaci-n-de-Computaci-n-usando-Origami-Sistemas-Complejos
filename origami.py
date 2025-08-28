# origami_half_only.py
"""
Archivo autocontenido: HALF-ADDER 

Incluye:
 - Pleat, Gadget (NOT, AND, OR, NAND)
 - XOR implementado por composición: XOR(a,b) = (a OR b) AND NOT(a AND b)
 - Half-adder: sum = XOR(a,b), carry = AND(a,b)
 - Tests: tablas de verdad para NOT/AND/OR/NAND, prueba XOR por composición,
          prueba de integración half-adder (4 combinaciones) y manejo de None.
 - LOS TESTS IMPRIMEN las tablas de verdad/resultados antes de hacer las aserciones.
 - Demo que imprime la tabla del half-adder y guarda half_adder_results.json

"""
from abc import ABC, abstractmethod
from collections import deque, defaultdict
from typing import Dict, List, Optional, Any, Set, Tuple
import json
import unittest

# ----------------------------
# Core: Pleat y Gadgets
# ----------------------------
class Pleat:
    def __init__(self, name: str, signal: Optional[bool] = None):
        self.name = name
        self.signal = signal
    def __repr__(self):
        return f"Pleat('{self.name}', {self.signal})"

class Gadget(ABC):
    def __init__(self, gadget_id: str, input_names: List[str], output_names: List[str]):
        self.gadget_id = gadget_id
        self.input_names = input_names
        self.output_names = output_names
        self.inputs: List[Pleat] = []
        self.outputs: List[Pleat] = []

    def connect_inputs(self, pleats_dict: Dict[str, Pleat]):
        for name in self.input_names:
            if name not in pleats_dict:
                raise ValueError(f"Pleat de entrada '{name}' no encontrado para gadget {self.gadget_id}")
            self.inputs.append(pleats_dict[name])

    def connect_outputs(self, pleats_dict: Dict[str, Pleat]):
        for name in self.output_names:
            if name not in pleats_dict:
                pleats_dict[name] = Pleat(name)
            self.outputs.append(pleats_dict[name])

    @abstractmethod
    def evaluate(self):
        pass

    def has_undefined_inputs(self) -> bool:
        return any(p.signal is None for p in self.inputs)

# Puertas básicas
class NOTGadget(Gadget):
    def __init__(self, gadget_id: str, input_name: str, output_name: str):
        super().__init__(gadget_id, [input_name], [output_name])
    def evaluate(self):
        if self.has_undefined_inputs():
            self.outputs[0].signal = None
        else:
            self.outputs[0].signal = not self.inputs[0].signal

class ANDGadget(Gadget):
    def __init__(self, gadget_id: str, input1: str, input2: str, output: str):
        super().__init__(gadget_id, [input1, input2], [output])
    def evaluate(self):
        if self.has_undefined_inputs():
            self.outputs[0].signal = None
        else:
            self.outputs[0].signal = self.inputs[0].signal and self.inputs[1].signal

class ORGadget(Gadget):
    def __init__(self, gadget_id: str, input1: str, input2: str, output: str):
        super().__init__(gadget_id, [input1, input2], [output])
    def evaluate(self):
        if self.has_undefined_inputs():
            self.outputs[0].signal = None
        else:
            self.outputs[0].signal = self.inputs[0].signal or self.inputs[1].signal

class NANDGadget(Gadget):
    def __init__(self, gadget_id: str, input1: str, input2: str, output: str):
        super().__init__(gadget_id, [input1, input2], [output])
    def evaluate(self):
        if self.has_undefined_inputs():
            self.outputs[0].signal = None
        else:
            self.outputs[0].signal = not (self.inputs[0].signal and self.inputs[1].signal)

# ----------------------------
# Network: conexión y ejecución
# ----------------------------
class Network:
    def __init__(self):
        self.pleats: Dict[str, Pleat] = {}
        self.gadgets: List[Gadget] = []

    def add_pleat(self, name: str, signal: Optional[bool] = None):
        self.pleats[name] = Pleat(name, signal)

    def add_gadget(self, gadget: Gadget):
        gadget.connect_inputs(self.pleats)
        gadget.connect_outputs(self.pleats)
        self.gadgets.append(gadget)

    def set_inputs(self, input_dict: Dict[str, Optional[bool]]):
        for name, signal in input_dict.items():
            if name in self.pleats:
                self.pleats[name].signal = signal
            else:
                self.add_pleat(name, signal)

    def topological_sort(self) -> List[Gadget]:
        pleat_to_producer: Dict[str, str] = {}
        for g in self.gadgets:
            for out in g.output_names:
                pleat_to_producer[out] = g.gadget_id

        graph: Dict[str, Set[str]] = defaultdict(set)
        in_degree: Dict[str, int] = {g.gadget_id: 0 for g in self.gadgets}
        gadget_map = {g.gadget_id: g for g in self.gadgets}

        for g in self.gadgets:
            consumer = g.gadget_id
            for inp in g.input_names:
                producer = pleat_to_producer.get(inp)
                if producer and producer != consumer:
                    if consumer not in graph[producer]:
                        graph[producer].add(consumer)
                        in_degree[consumer] += 1

        queue = deque([gid for gid, deg in in_degree.items() if deg == 0])
        order: List[Gadget] = []
        while queue:
            gid = queue.popleft()
            order.append(gadget_map[gid])
            for nbr in graph.get(gid, []):
                in_degree[nbr] -= 1
                if in_degree[nbr] == 0:
                    queue.append(nbr)

        if len(order) != len(self.gadgets):
            raise ValueError("Ciclo de dependencias detectado en la red")
        return order

    def run(self, max_iterations: int = 5, trace: bool = False) -> Dict[str, Optional[bool]]:
        execution_order = self.topological_sort()
        if trace:
            print("Orden topológico:", [g.gadget_id for g in execution_order])
        for iteration in range(max_iterations):
            changed = False
            if trace:
                print(f"Iteración {iteration+1}:")
            for g in execution_order:
                old = [o.signal for o in g.outputs]
                g.evaluate()
                new = [o.signal for o in g.outputs]
                if trace and old != new:
                    print(f" {g.gadget_id} -> {[(o.name,o.signal) for o in g.outputs]}")
                if old != new:
                    changed = True
            if not changed:
                if trace:
                    print("Convergió.")
                break
        return {name: p.signal for name, p in self.pleats.items()}

# ----------------------------
# Half-adder (XOR por composición)
# ----------------------------
def build_half_adder_network() -> Network:
    """
    Pleats:
      entradas: "a", "b"
      temporales: "and_temp", "or_temp", "not_temp"
      salidas: "sum", "carry"
    """
    net = Network()
    for name in ["a","b","and_temp","or_temp","not_temp","sum","carry"]:
        net.add_pleat(name)
    # XOR por composición: (a OR b) AND NOT(a AND b)
    net.add_gadget(ANDGadget("and1", "a", "b", "and_temp"))
    net.add_gadget(ORGadget("or1", "a", "b", "or_temp"))
    net.add_gadget(NOTGadget("not1", "and_temp", "not_temp"))
    net.add_gadget(ANDGadget("and2", "or_temp", "not_temp", "sum"))
    # carry
    net.add_gadget(ANDGadget("and3_carry", "a", "b", "carry"))
    return net

def run_half_adder_table(save_json: bool = False, path: str = "half_adder_results.json", trace: bool = False):
    net = build_half_adder_network()
    combos = [(False,False),(False,True),(True,False),(True,True)]
    expected = {
        (False,False):(False,False),
        (False,True):(True,False),
        (True,False):(True,False),
        (True,True):(False,True),
    }
    results: Dict[str, Any] = {}
    print("\nHalf-adder truth table (sum = XOR(a,b), carry = AND(a,b))")
    print(" a | b | sum | carry | expected | ok")
    print("---+---+-----+-------+----------+----")
    for a,b in combos:
        net.set_inputs({"a": a, "b": b})
        snapshot = net.run(trace=trace)
        s = snapshot.get("sum")
        c = snapshot.get("carry")
        exp_s, exp_c = expected[(a,b)]
        ok = (s == exp_s) and (c == exp_c)
        key = f"{int(a)}{int(b)}"   # "00","01","10","11" for JSON friendliness
        results[key] = {"a": a, "b": b, "sum": s, "carry": c, "expected_sum": exp_s, "expected_carry": exp_c, "ok": ok}
        print(f" {int(a)} | {int(b)} |  {int(s) if s is not None else 'N'}  |   {int(c) if c is not None else 'N'}   |   {int(exp_s)},{int(exp_c)}   | {ok}")

    if save_json:
        with open(path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResultados guardados en {path}")
    return results

# ----------------------------
# Helpers para imprimir tablas en tests
# ----------------------------
def _print_table_two_inputs(rows: List[Tuple[int,int,int]], title: str, output_name: str):
    # rows: list of (a,b,out)
    print(f"\n{title}")
    print(" a | b | {} ".format(output_name))
    print("---+---+---")
    for a,b,out in rows:
        print(f" {int(a)} | {int(b)} |  {int(out) if out is not None else 'N'}")

def _print_table_not(rows: List[Tuple[int,int]], title: str, output_name: str):
    # rows: list of (a,out)
    print(f"\n{title}")
    print(" a | {} ".format(output_name))
    print("---+---")
    for a,out in rows:
        print(f" {int(a)} |  {int(out) if out is not None else 'N'}")

# ----------------------------
# Tests unitarios (solo half-adder / gates)
# ----------------------------
class Test_Gates_TruthTables(unittest.TestCase):
    def test_not(self):
        net = Network(); net.add_pleat("a"); net.add_pleat("out")
        net.add_gadget(NOTGadget("n1","a","out"))
        rows = []
        for a, exp in [(False, True),(True, False)]:
            net.set_inputs({"a": a})
            res = net.run()
            out = res["out"]
            rows.append((a, out))
        # Imprimir tabla de verdad para NOT
        _print_table_not(rows, "Tabla de verdad: NOT", "out")
        # Aserciones
        for (a, out), (_, exp) in zip(rows, [(False, True),(True, False)]):
            self.assertEqual(out, exp)

    def test_and(self):
        net = Network(); net.add_pleat("a"); net.add_pleat("b"); net.add_pleat("out")
        net.add_gadget(ANDGadget("and1","a","b","out"))
        rows = []
        for a in [False, True]:
            for b in [False, True]:
                net.set_inputs({"a": a, "b": b})
                res = net.run()
                rows.append((a, b, res["out"]))
        _print_table_two_inputs(rows, "Tabla de verdad: AND", "out")
        # Aserciones
        for a,b,out in rows:
            self.assertEqual(out, a and b)

    def test_or(self):
        net = Network(); net.add_pleat("a"); net.add_pleat("b"); net.add_pleat("out")
        net.add_gadget(ORGadget("or1","a","b","out"))
        rows = []
        for a in [False, True]:
            for b in [False, True]:
                net.set_inputs({"a": a, "b": b})
                res = net.run()
                rows.append((a, b, res["out"]))
        _print_table_two_inputs(rows, "Tabla de verdad: OR", "out")
        # Aserciones
        for a,b,out in rows:
            self.assertEqual(out, a or b)

    def test_nand(self):
        net = Network(); net.add_pleat("a"); net.add_pleat("b"); net.add_pleat("out")
        net.add_gadget(NANDGadget("nand1","a","b","out"))
        rows = []
        for a in [False, True]:
            for b in [False, True]:
                net.set_inputs({"a": a, "b": b})
                res = net.run()
                rows.append((a, b, res["out"]))
        _print_table_two_inputs(rows, "Tabla de verdad: NAND", "out")
        # Aserciones
        for a,b,out in rows:
            self.assertEqual(out, not (a and b))

    def test_xor_composition(self):
        net = Network()
        for name in ["a","b","and_temp","or_temp","not_temp","out"]:
            net.add_pleat(name)
        # XOR composition
        net.add_gadget(ANDGadget("and1","a","b","and_temp"))
        net.add_gadget(ORGadget("or1","a","b","or_temp"))
        net.add_gadget(NOTGadget("not1","and_temp","not_temp"))
        net.add_gadget(ANDGadget("and2","or_temp","not_temp","out"))
        rows = []
        for a in [False, True]:
            for b in [False, True]:
                net.set_inputs({"a": a, "b": b})
                res = net.run()
                rows.append((a, b, res["out"]))
        _print_table_two_inputs(rows, "Tabla de verdad: XOR (por composición)", "out")
        # Aserciones
        for a,b,out in rows:
            expected = (a or b) and not (a and b)
            self.assertEqual(out, expected)

class Test_HalfAdder_Integration(unittest.TestCase):
    def test_half_adder_all(self):
        net = build_half_adder_network()
        rows = []
        expected_cases = {
            (False,False):(False,False),
            (False,True):(True,False),
            (True,False):(True,False),
            (True,True):(False,True)
        }
        for (a,b), (es,ec) in expected_cases.items():
            net.set_inputs({"a": a, "b": b})
            res = net.run()
            rows.append((a, b, res.get("sum"), res.get("carry"), es, ec))
        # Imprimir tabla del half-adder
        print("\nTabla del Half-adder (sum = XOR(a,b), carry = AND(a,b))")
        print(" a | b | sum | carry | expected_sum,expected_carry | ok")
        print("---+---+-----+-------+---------------------------+----")
        for a,b,s,c,es,ec in rows:
            ok = (s == es and c == ec)
            print(f" {int(a)} | {int(b)} |  {int(s) if s is not None else 'N'}  |   {int(c) if c is not None else 'N'}   |    {int(es)},{int(ec)}    | {ok}")
        # Aserciones
        for a,b,s,c,es,ec in rows:
            self.assertEqual(s, es)
            self.assertEqual(c, ec)

class Test_Undefined_Minimal(unittest.TestCase):
    def test_and_none(self):
        net = Network(); net.add_pleat("a", None); net.add_pleat("b", True); net.add_pleat("c")
        net.add_gadget(ANDGadget("and1","a","b","c"))
        res = net.run()
        print("\nTest señales indefinidas: AND con entrada None -> salida debe ser None")
        print(f" a=None, b=True -> c={res['c']}")
        self.assertIsNone(res["c"])

# ----------------------------
# Main: ejecutar tests y demo
# ----------------------------
def main_demo():
    print("Demo half-adder (XOR por composición):")
    run_half_adder_table(save_json=True, path="half_adder_results.json", trace=False)
    print("\nArchivo JSON 'half_adder_results.json' creado.")

if __name__ == "__main__":
    # Ejecuta SOLO los tests incluidos en este archivo
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
    print("\n--- Demo ---")
    main_demo()
