# traffic_sym

- Andrés Tarazona - A01023332
- Alejandro Arouesty - A01782691

## Descripción
En este proyecto se utiliza un API escrito en Python, con Flask, que maneja la logica de movimiento de entidades instanciadas de coches dentro de un proyecto de Unity. 

En este mismo se desarrolla una simulación que presenta el movimiento de los mismos, junto con una representación de la ciudad donde están moviéndose los mismos.

> El punto de este proyecto es entender el funcionamiento de los sistemas multiagentes, y de las representaciones gráficas en las computadoras.

## Tecnologías Utilizadas
### Python
- [`Flask`](https://flask.palletsprojects.com/en/3.0.x/)
- [`Mesa`](https://mesa.readthedocs.io/en/stable/)

### C Sharp
- [`Unity`](https://unity.com/)

## Utilización de repositorio

Para correr el servidor:

```zsh
python3 server.py  
```

Este comando inicializa el servidor de Flask, al que se conectará el Unity directamente a través de localhost.
