#%%ñibrerias
import sys
#Qfiledialog es una ventana para abrir yu gfuardar archivos
#Qvbox es un organizador de widget en la ventana, este en particular los apila en vertcal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QFileDialog
from PyQt5 import QtCore, QtWidgets

from matplotlib.figure import Figure
import keyboard
from PyQt5.uic import loadUi
import matplotlib.pyplot as plt
from numpy import arange, sin, pi
#contenido para graficos de matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pyqtgraph as pg
import serial, time
import numpy as np

# clase con el lienzo (canvas=lienzo) para mostrar en la interfaz los graficos matplotlib, el canvas mete la grafica dentro de la interfaz
class MyGraphCanvas(FigureCanvas):
    #constructor
    def __init__(self, parent= None,width=5, height=4, dpi=100):
        
        #se crea un objeto figura
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #el axes en donde va a estar mi grafico debe estar en mi figura
        self.axes = self.fig.add_subplot(111)
        
        #llamo al metodo para crear el primer grafico
        self.compute_initial_figure()
        
        #se inicializa la clase FigureCanvas con el objeto fig
                # Instanciar figura
        FigureCanvas.__init__(self,self.fig)
        
    #este metodo me grafica al senal senoidal que yo veo al principio, mas no senales
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t,s)
    #hay que crear un metodo para graficar lo que quiera
    def graficar_datos(self,datos):
        #primero se necesita limpiar la grafica anterior
        self.axes.clear()
        #ingresamos los datos a graficar
        self.axes.plot(datos)
        #y lo graficamos
        #print("datos")
        #print(datos)
        #voy a graficar en un mismo plano varias senales que no quecden superpuestas cuando uso plot me pone las graficas en un mismo grafico
        for c in range(datos.shape[0]):
            self.axes.plot(datos[c]+10)
        self.axes.set_xlabel("Muestras")
        self.axes.set_ylabel("Amplitud (mV)")
        #self.axes.set
        #ordenamos que dibuje
        self.axes.figure.canvas.draw()
#%%
        #es una clase que yop defino para crear los intefaces graficos
class InterfazGrafico(QMainWindow):
    #condtructor
    def __init__(self):
        #siempre va
        super(InterfazGrafico,self).__init__()
        #se carga el diseno
        loadUi ('anadir_grafico.ui',self)
        #se llama la rutina donde configuramos la interfaz
        self.setup()
        #se muestra la interfaz
        self.show()
    def setup(self):
        #los layout permiten organizar widgets en un contenedor
        #esta clase permite añadir widget uno encima del otro (vertical)
        layout = QVBoxLayout()
        #se añade el organizador al campo grafico
        self.campo_grafico.setLayout(layout)
        #se crea un objeto para manejo de graficos
        self.__sc = MyGraphCanvas(self.campo_grafico, width=5, height=4, dpi=100)
        #se añade el campo de graficos
        layout.addWidget(self.__sc)
        
        #se organizan las señales 
        self.boton_cargar.clicked.connect(self.cargar_senal)
        self.boton_continuar.clicked.connect(self.continuar_senal)
        self.boton_detener.clicked.connect(self.detener)
        self.boton_adelante.clicked.connect(self.adelante_senal)
        self.boton_atras.clicked.connect(self.atrasar_senal)
        self.boton_aumentar.clicked.connect(self.aumentar_senal)
        self.boton_disminuir.clicked.connect(self.disminuir_senal)    
        #hay botones que no deberian estar habilitados si no he cargado la senal
        self.boton_adelante.setEnabled(False)
        self.boton_atras.setEnabled(False)
        self.boton_aumentar.setEnabled(False)
        self.boton_disminuir.setEnabled(False)
        self.boton_continuar.setEnabled(False)
        self.boton_detener.setEnabled(False)
        if self.EXG.currentText() == 'ECG':
            self.n = 100
        elif self.EXG.currentText() == 'EMG':
            self.n = 500
        #cuando cargue la senal debo volver a habilitarlos
        p=self.puertos_seriales()
        #self.arduino = serial.Serial(p[1],9600,timeout=0.01)# Se debe indicar el puerto serial y la velocidad de transmisión 
        for com in p:
            try:
                self.arduino = serial.Serial(com,9600,timeout=0.01)# Se debe indicar el puerto serial y la velocidad de transmisión 
            except:
                pass
        
    def asignar_Controlador(self,controlador):
        self.__coordinador=controlador
    def adelante_senal(self):
        self.__x_min=self.__x_min+self.n
        self.__x_max=self.__x_max+self.n
        self.__sc.graficar_datos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
    def atrasar_senal(self):
        #que se salga de la rutina si no puede atrazar
        if self.__x_min<100:
            return
        self.__x_min=self.__x_min-self.n
        self.__x_max=self.__x_max-self.n
        self.__sc.graficar_datos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
    def aumentar_senal(self):
        #en realidad solo necesito limites cuando tengo que extraerlos, pero si los 
        #extraigo por fuera mi funcion de grafico puede leer los valores
        self.__sc.graficar_datos(self.__coordinador.escalarSenal(self.__x_min,self.__x_max,100))
    def disminuir_senal(self):
        self.__sc.graficar_datos(self.__coordinador.escalarSenal(self.__x_min,self.__x_max,1/100))

    def puertos_seriales(self):
        ports = ['COM%s' % (i + 1) for i in range(256)]
        encontrados = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                encontrados.append(port)
            except (OSError, serial.SerialException):
                pass
        return encontrados
    
    def cargar_senal(self):
        self.senal('1')

    def continuar_senal(self):
        self.senal('2',self.EMG)


    def senal(self,m,EMG=None):
        '''
        Start sending the data, use the subprocess.Popen function to start a
        new process without stopping the existing one.
        '''
        time.sleep(2)
        if m == '1':
            self.EMG = np.ndarray((0),dtype=np.int) # aquí se almacenará la señal  
            numero_datos = 5000       
        elif m == '2':
            self.EMG = EMG
            numero_datos = 5000 + len(EMG)
        else:
            pass
             
            

        # mientras el arreglo no tenga los datos que requiero los solicito
         # esto corresponde al numero de datos que se va adquirir, se puede modificar pero 1000 es un buen numero 
        while self.EMG.shape[0] < numero_datos: 
            
            # esto lee lo que haya en el buffer
            datos = self.arduino.readlines(self.arduino.inWaiting())
            
            datos_por_leer = len(datos)
            
        
            # Si hay mas datos de los que quiero leer
            # solo me quedo con la cantidad que me interesa
            if len(datos) > numero_datos:
                datos = datos[0:numero_datos]
                # creo un arreglo de ceros para leer estos valores
                valores_leidos = np.zeros(numero_datos,dtype = np.int)
            else:
                # creo un arreglo de ceros para leer estos valores
                valores_leidos = np.zeros(datos_por_leer,dtype = np.int)

            
            posicion = 0
            #se convierten los datos a valores numericos de voltaje. 
            for dato in datos:
                # voy a tratar de convertir los datos
                try:
                    # elimino los saltos de linea y caracter de retorno y convierto a entero
                    valores_leidos[posicion] = int(dato.decode().strip())
                except:
                    # si no puedo convertir completo la muestra con el anterior
                    # valores_leidos[posicion] = 0  # alternativa
                    valores_leidos[posicion] = valores_leidos[posicion-1]
                posicion = posicion + 1
            # agrego los datos leidos al arreglo
            self.EMG = np.append(self.EMG,valores_leidos)
            # Introduzco un delay para que se llene de nuevo el buffer
            time.sleep(2)

        # como la ultima lectura puede tener mas datos de los que necesito descarto las muestras restantes
        #EMG = EMG[0:numero_datos]
        # ya con los datos leidos podemos graficar
        #plt.plot(EMG)
        #plt.show()
        #se abre el cuadro de dialogo para cargar
        #el coordinador recibe y guarda la senal en su propio .py, por eso no 
        #necesito una variable que lo guarde en el .py interfaz
        self.__coordinador.recibirDatosSenal(self.EMG)
        self.__x_min=0
        self.__x_max=2000
        #graficar utilizando el controlador
        self.__sc.graficar_datos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
        self.boton_adelante.setEnabled(True)
        self.boton_atras.setEnabled(True)
        self.boton_aumentar.setEnabled(True)
        self.boton_disminuir.setEnabled(True)
        self.boton_continuar.setEnabled(True)
        self.boton_detener.setEnabled(True)
        #self.boton_cargar.setEnabled(False)
        scene = QtWidgets.QGraphicsScene()
        self.cuadro_grafico.setScene(scene)
        self.plt = pg.PlotWidget()
        plot_item = self.plt.plot(self.EMG)
        proxy_widget = scene.addWidget(self.plt)
    

    def detener(self):
        self.boton_cargar.setEnabled(False)
        self.boton_continuar.setEnabled(False)
        self.boton_detener.setEnabled(False)
        self.arduino.close()  # Cerrar puerto serial, siempre debe cerrarse
#        
#app=QApplication(sys.argv)
#mi_ventana = InterfazGrafico()
#sys.exit(app.exec_()) 
#               
        