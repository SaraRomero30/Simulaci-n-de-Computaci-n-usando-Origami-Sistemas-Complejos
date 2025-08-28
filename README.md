# Simualación Computación con Origami

## Overview
Este proyecto implementa un **circuito half-adder digital** usando un modelo de cómputo "origami", donde las operaciones lógicas se realizan a través de estructuras plegadas llamadas **pleats** y **gadgets**.  

La implementación incluye compuertas lógicas básicas (**NOT, AND, OR, NAND**) y las combina para crear un circuito half-adder que calcula tanto la **suma (XOR)** como el **acarreo (AND)**.

---

## Core Concepts

### Pleats
- Los **pleats** representan los portadores fundamentales de señales en el sistema.  
- Cada pleat:
  - Tiene un nombre.  
  - Puede contener un valor booleano (`True/False`) o ser indefinido (`None`).  
- Funcionan como entradas y salidas para los gadgets lógicos.  

### Gadgets
Los **gadgets** son operadores lógicos que transforman señales:  

- `NOTGadget`: Negación (1 entrada).  
- `ANDGadget`: Operación AND (2 entradas).  
- `ORGadget`: Operación OR (2 entradas).  
- `NANDGadget`: Operación NAND (2 entradas).  

Cada gadget:
- Se conecta a pleats de entrada y salida.  
- Implementa un método `evaluate()` que calcula su salida en base a los valores actuales de entrada.  

### Network
La clase `Network` administra el circuito completo:  

- Mantiene la colección de pleats y gadgets.  
- Maneja las conexiones entre componentes.  
- Realiza **ordenamiento topológico** para determinar el orden de evaluación.  
- Ejecuta el circuito iterativamente hasta que las señales se estabilicen.  

---

## Half-Adder Implementation

El **half-adder** se construye mediante composición de compuertas básicas:

```text
sum   = (a OR b) AND NOT(a AND b)   # Implementación XOR
carry = a AND b
```

--- 

## Test Results
Basic Gate Truth Tables

NOT Gate
| a | out |
| - | --- |
| 0 | 1   |
| 1 | 0   |

AND Gate
| a | b | out |
| - | - | --- |
| 0 | 0 | 0   |
| 0 | 1 | 0   |
| 1 | 0 | 0   |
| 1 | 1 | 1   |

OR Gate
| a | b | out |
| - | - | --- |
| 0 | 0 | 0   |
| 0 | 1 | 1   |
| 1 | 0 | 1   |
| 1 | 1 | 1   |

NAND Gate
| a | b | out |
| - | - | --- |
| 0 | 0 | 1   |
| 0 | 1 | 1   |
| 1 | 0 | 1   |
| 1 | 1 | 0   |

XOR Implementation (Gate Composition)
| a | b | out |
| - | - | --- |
| 0 | 0 | 0   |
| 0 | 1 | 1   |
| 1 | 0 | 1   |
| 1 | 1 | 0   |

Half-Adder Integration Test
| a | b | sum | carry | expected | ok |
| - | - | --- | ----- | -------- | -- |
| 0 | 0 | 0   | 0     | 0,0      | ✓  |
| 0 | 1 | 1   | 0     | 1,0      | ✓  |
| 1 | 0 | 1   | 0     | 1,0      | ✓  |
| 1 | 1 | 0   | 1     | 0,1      | ✓  |

---

Edge Case Handling
La implementación maneja correctamente entradas indefinidas (None):

Ejemplo: operación AND con un input indefinido
a=None, b=True → c=None

--- 

## Execution and Output
Cuando se ejecuta el programa:
- Se corren los tests unitarios para verificar el comportamiento correcto.
- Se generan las tablas de verdad para el half-adder.
- Se guardan los resultados detallados en half_adder_results.json.

---

## Technical Details
- Topological Sorting: La red utiliza el algoritmo de Kahn para ordenar topológicamente los gadgets y asegurar que las entradas se calculen antes de ser usadas por gadgets dependientes.

- Iterative Evaluation: El circuito se evalúa iterativamente hasta que las señales se estabilizan o se alcanza un número máximo de iteraciones, soportando bucles de retroalimentación en circuitos más complejos.

- Extensibility: La arquitectura permite agregar nuevos tipos de gadgets extendiendo la clase base Gadget e implementando el método evaluate().

--- 

## Uso
Ejecutar la implementación directamente:

```python
python origami.py
```
