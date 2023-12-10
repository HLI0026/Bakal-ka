#qiskit                                    0.41.0
#qiskit-aer                                0.11.2
#qiskit-ibmq-provider                      0.20.0
#qiskit-terra                              0.23.1

from qiskit import Aer, assemble, transpile
from qiskit import QuantumCircuit
import math

def compute_iter(n,m) -> int:
    """
    Computes the number of iterations for the Grover's algorithm
    """
    return math.floor(math.pi*math.sqrt(2**n/m)/4-1/2)

def large_solution(shots)-> dict:    
    """
    Runs simulator on large problem, returns dictionary with relative counts
    """

    oracle=QuantumCircuit(16)
    ############################################
    #For rows in lattice
    oracle.cx(0,9)
    oracle.cx(1,9)
    oracle.cx(2,9)
    oracle.mcx([0,1,2],9)

    oracle.cx(3,10)
    oracle.cx(4,10)
    oracle.cx(5,10)
    oracle.mcx([3,4,5],10)

    oracle.cx(6,11)
    oracle.cx(7,11)
    oracle.cx(8,11)
    oracle.mcx([6,7,8],11)
    ############################################
    #For cols in lattice
    oracle.cx(0,12)
    oracle.cx(3,12)
    oracle.cx(6,12)
    oracle.mcx([0,3,6],12)

    oracle.cx(1,13)
    oracle.cx(4,13)
    oracle.cx(7,13)
    oracle.mcx([1,4,7],13)

    oracle.cx(2,14)
    oracle.cx(5,14)
    oracle.cx(8,14)
    oracle.mcx([2,5,8],14)
    ############################################

    oracle.mcx([9,10,11,12,13,14],15)
    ############################################
    #For rows in lattice
    oracle.cx(0,9)
    oracle.cx(1,9)
    oracle.cx(2,9)
    oracle.mcx([0,1,2],9)

    oracle.cx(3,10)
    oracle.cx(4,10)
    oracle.cx(5,10)
    oracle.mcx([3,4,5],10)

    oracle.cx(6,11)
    oracle.cx(7,11)
    oracle.cx(8,11)
    oracle.mcx([6,7,8],11)
    ############################################
    #For cols in lattice
    oracle.cx(0,12)
    oracle.cx(3,12)
    oracle.cx(6,12)
    oracle.mcx([0,3,6],12)

    oracle.cx(1,13)
    oracle.cx(4,13)
    oracle.cx(7,13)
    oracle.mcx([1,4,7],13)

    oracle.cx(2,14)
    oracle.cx(5,14)
    oracle.cx(8,14)
    oracle.mcx([2,5,8],14)
    ############################################

    oracle= oracle.to_gate()

    diffuser = QuantumCircuit(16)
    diffuser.h(range(9))
    diffuser.x(range(9))
    diffuser.mcx(list(range(9)),15)
    diffuser.x(range(9))
    diffuser.h(range(9))
    diffuser=diffuser.to_gate()

    ############################################

    qc= QuantumCircuit(16,9)
    
    for i in range(9):
        qc.h(i)
    qc.x(15)
    qc.h(15)
    iters = compute_iter(9,6)
    
    for i in range(iters):
        qc.append(oracle,list(range(16)))
        qc.append(diffuser,list(range(16)))

    qc.x(range(9))

    qc.measure(list(range(9)), list(range(9)))

    aer_sim = Aer.get_backend('aer_simulator')
    trans_circ = transpile(qc, aer_sim)
    assembled = assemble(trans_circ,shots=shots)
    result = aer_sim.run(assembled).result()
    counts = result.get_counts()
    
    return {key:val/shots for key, val in counts.items()}
def small_soluction_0(shots)-> dict:
    """
    Runs simulator on small problem with first approach, returns dictionary with relative counts
    """
    diffuser = QuantumCircuit(6)
    diffuser.h(range(4))
    diffuser.x(range(4))
    diffuser.mcx(list(range(4)),5)
    diffuser.x(range(4))
    diffuser.h(range(4))
    diffuser=diffuser.to_gate()

    oracle=QuantumCircuit(6)
    oracle.cx(0,4)
    oracle.cx(1,4)
    oracle.cx(0,2)
    oracle.cx(1,3)
    oracle.mcx([2,3,4],5)
    oracle.cx(0,4)
    oracle.cx(1,4)
    oracle.cx(0,2)
    oracle.cx(1,3)
    oracle = oracle.to_gate()

    qc= QuantumCircuit(6,4)
    for i in range(4):
        qc.h(i)
    qc.x(5)
    qc.h(5)
    iters = compute_iter(4,2)
    for i in range(iters):
        qc.append(oracle,list(range(6)))
        qc.append(diffuser,list(range(6)))

    qc.measure(list(range(4)), list(range(4)))
    aer_sim = Aer.get_backend('aer_simulator')
    trans_circ = transpile(qc, aer_sim)
    assembled = assemble(trans_circ,shots=shots)
    result = aer_sim.run(assembled).result()
    counts = result.get_counts()
    return {key:val/shots for key, val in counts.items()}

def small_soluction_1(shots)-> dict:
    """
    Runs simulator on small problem with second approach, returns dictionary with relative counts
    """
    diffuser = QuantumCircuit(5)
    diffuser.h(range(4))
    diffuser.x(range(4))
    diffuser.mcx(list(range(4)), 4)
    diffuser.x(range(4))
    diffuser.h(range(4))
    diffuser = diffuser.to_gate()

    oracle = QuantumCircuit(5)
    oracle.x(0)
    oracle.x(3)
    oracle.mcx(list(range(4)), 4)
    oracle.x(0)
    oracle.x(3)
    oracle.x(1)
    oracle.x(2)
    oracle.mcx(list(range(4)), 4)
    oracle.x(1)
    oracle.x(2)

    qc = QuantumCircuit(5, 4)

    for i in range(4):
        qc.h(i)
    qc.x(4)
    qc.h(4)
    iters = compute_iter(4, 2)
    for i in range(iters):
        qc.append(oracle, list(range(5)))
        qc.append(diffuser, list(range(5)))

    qc.measure(list(range(4)), list(range(4)))
    aer_sim = Aer.get_backend('aer_simulator')
    trans_circ = transpile(qc, aer_sim)
    assembled = assemble(trans_circ, shots=shots)
    result = aer_sim.run(assembled).result()
    counts = result.get_counts()
    return {key: val / shots for key, val in counts.items()}