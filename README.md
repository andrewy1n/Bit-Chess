<h3 align="center">Bit-Chess</h3>

</div>

---

<p align="center"> Bitboard implementation for Chess in Python
    <br> 
</p>

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Built Using](#built_using)
- [Acknowledgments](#acknowledgement)

## About <a name = "about"></a>

This project implements Chess bitboards using NumPy 64-bit integers and various NumPy array functions for rotated bitboard implementation. This process is used to store all possible orthogonal and diagonal moves, and their respective blocker formations calculated as a unique index. A legal move generator is created by keeping track of pinned pieces and other game conditions to reduce the need for recalculating opposing attacks.

## Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Installing

```
pip install bit-chess-python
```

## Usage <a name="usage"></a>

If you want to run PERFT, import the PERFT class and call the perft function:

```
from BitChess import Perft
perft = Perft(FEN_string)
perft.perft(1)
```

## Built Using <a name = "built_using"></a>

- NumPy
- gmpy2

## Acknowledgements <a name = "acknowledgement"></a>

- Inspired by Sebastian Logue's [Chess-Coding-Adventures](https://github.com/SebLague/Chess-Coding-Adventure)
- Rotated Bitboards [pdf](https://www.cs.cmu.edu/afs/cs/academic/class/15418-s12/www/competition/www.contrib.andrew.cmu.edu/~jvirdo/rasmussen-2004.pdf)
