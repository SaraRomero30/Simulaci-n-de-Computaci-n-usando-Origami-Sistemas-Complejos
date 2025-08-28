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
