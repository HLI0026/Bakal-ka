import numpy as np
from qiskit import Aer, assemble, transpile
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram 

%Dependencies:

%qiskit                                    0.41.0
%qiskit-aer                                0.11.2
%qiskit-ibmq-provider                      0.20.0
%qiskit-terra                              0.23.1
%numpy                                     1.23.5

class GroversAlgorithm:
    """
    This is main class to store data and circuit for solving inputted data
    """


    def __init__(self, clauses_path:str, shots:int) -> None:
        """
        _shots: number of shots for simulation
        _clauses_path: path to file with clauses
        _clauses: list of clauses
        _diffuser_qubits_count: number of qubits needed for diffuser
        _clause_qubits_count: number of qubits needed for clause realization
        _all_qubits_count: number of all qubits needed
        
        """
        self._shots = shots
        self._clauses_path = clauses_path
        self._clauses = self.file_read()
        self.qubits_counts()

        self._init_gate = None
        self._oracle_gate = None
        self._diffuser_gate = None
        self._init_gate_realization = None
        self._oracle_gate_realization = None
        self._diffuser_gate_realization = None
        self._counts = None

    def circuit_setup(self) ->None:
        """
        _init_gate: gate, which sets correct qubits into superposition and last qubits into |-> state
        _oracle: gate, which marks correct item(s)
        _diffuser: gate, which inverts amplitudes of marked items
        """
        self._init_gate_realization = self.init()
        self._init_gate = self._init_gate_realization.to_gate()
        self._init_gate.name = "init"
        self._oracle_gate_realization = self.oracle()
        self._oracle_gate = self._oracle_gate_realization.to_gate()
        self._oracle_gate.name = "oracle"
        self._diffuser_gate_realization = self.diffuser()
        self._diffuser_gate = self._diffuser_gate_realization.to_gate()
        self._diffuser_gate.name = "diffuser"

    def file_read(self) -> list:
        """
        Reading file, transfering from string to list of lists, which contain single clauses
        """
        clauses = ""
        my_file = open(self._clauses_path, "rt")
        #reading file
        for line in my_file:
            clauses += line
        
        clauses = clauses.rsplit()
        #From string to list
        clauses_int=[]

        for idx, clause in enumerate(clauses):
            cls = clause.split(",")
            clauses_int.append([int(cls[0]) , int(cls[1])])

        my_file.close()

        return clauses_int


    def qubits_counts(self) -> None:
        """
        Sets up amount of qubits required for oracle and diffuser into self._diffuser_qubits_count and self._clause_qubits_count respectively
        Also sets up amount of all qubits into self._all_qubits_count
        """

        self._diffuser_qubits_count = 0
        self._clause_qubits_count = 0
        self._all_qubits_count = 0
        
        for cl1, cl2 in self._clauses:
            
            if self._diffuser_qubits_count<cl1:
                self._diffuser_qubits_count = cl1
            
            if self._diffuser_qubits_count<cl2:
                self._diffuser_qubits_count = cl2
        
        #due to 0 indexing of python we need to add 1 to diffuser qubits

        self._diffuser_qubits_count +=1
        self._clause_qubits_count = len(self._clauses)
        self._all_qubits_count  = self._clause_qubits_count+self._diffuser_qubits_count+1


    def init(self) ->QuantumCircuit: 
        """
        Returns gate, which sets correct qubits into superposition and last qubits into |-> state
        """
        qc = QuantumCircuit(self._all_qubits_count)

        for qubit in range(self._diffuser_qubits_count):
            qc.h(qubit)
    
        qc.x(self._all_qubits_count-1)
        qc.h(self._all_qubits_count-1)
        return qc

    def oracle(self) -> QuantumCircuit:
        """
        Makes oracle of grovers algorithm from clauses and respective amount of neccesary qubits
        Marks correct item(s)
        """
        qc = QuantumCircuit(self._all_qubits_count)
        for idx, clause in enumerate(self._clauses):
            qc.cx(clause[0], idx + self._clause_qubits_count)
            qc.cx(clause[1], idx + self._clause_qubits_count)

        qc.mct(list(range(self._diffuser_qubits_count, self._all_qubits_count-1)), self._all_qubits_count-1)
        
        for idx, clause in enumerate(self._clauses):
            qc.cx(clause[0], idx + self._clause_qubits_count)
            qc.cx(clause[1], idx + self._clause_qubits_count)

        return qc
    

    def diffuser(self)-> QuantumCircuit:
        """
        Diffuser amplifies probability of measuring marked items by oracle (or amplifies unmarked items - this depends on how many iterations of algorithm are done). Diffuser is built based on clauses.
        """
        qc = QuantumCircuit(self._diffuser_qubits_count)

        for i in range(self._diffuser_qubits_count-1):
            qc.h(i)
            qc.x(i)

        #qc.barrier(list(range(amount[0])))
        qc.z(self._diffuser_qubits_count-1)
        qc.mct(list(range(self._diffuser_qubits_count-1)), self._diffuser_qubits_count-1)
        qc.z(self._diffuser_qubits_count-1)
        #qc.barrier(list(range(amount[0])))
        for i in range(self._diffuser_qubits_count-1):
            qc.x(i)
            qc.h(i)

        return qc

    def grovers(self) -> None:
        """
        Runs grovers algorithm and returns counts of measured items
        Algorithm:
        1. Set correct qubits into superposition and last qubit into |-> state
        2. Run oracle for set up oracle part of grovers algorithm
        3. Run diffuser for set up diffuser part of grovers algorithm
        4. Measure diffuser qubits
        """

        iterations = int(np.arcsin(1/np.sqrt(self._diffuser_qubits_count)))#sometimes number of iterations can be near 0, in this case we increase it to 1 to make algorithm work
        if iterations == 0:
            iterations = 1
        
        init_qubits = list(range(self._all_qubits_count))
        oracle_qubits = list(range(self._all_qubits_count))
        diffuser_qubits = list(range(self._diffuser_qubits_count))
        #------------------------------------------------------------------#
        qc = QuantumCircuit(self._all_qubits_count,self._diffuser_qubits_count)
        qc.append(self._init_gate,init_qubits)

        for i in range(iterations):        
            qc.append(self._oracle_gate,oracle_qubits)
            qc.append(self._diffuser_gate, diffuser_qubits)
        
        qc.measure(diffuser_qubits,diffuser_qubits)
        #------------------------------------------------------------------#
        aer_sim = Aer.get_backend('aer_simulator')
        trans_circ = transpile(qc, aer_sim)
        assembled = assemble(trans_circ,shots=self._shots)
        results = aer_sim.run(assembled).result()
        
        self._counts = results.get_counts()


    def my_plot(self, path:( str | None) = None):
        """
        Plots the result of the simulation
        """
        if path:
            plot_histogram(self._counts, filename =path)
        else:
            return plot_histogram(self._counts)