# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Octavio Navarro. October 2023git

from flask import Flask, request, jsonify
from model import *
from agent import *
from model import CityModel
citymodel = None



number_agents = 10
width = 24
height = 25
currentStep = 0

app = Flask("Traffic example")

@app.route('/init', methods=['GET', 'POST'])
def initModel():
    global citymodel

    number_agents = int(request.form.get('NAgents', 10))
    width = int(request.form.get('width', 20))
    height = int(request.form.get('height', 20))
    currentStep = 0

    print(request.form)
    print(number_agents, width, height)
     ##   if CityModel is None: return
    citymodel = CityModel(number_agents)

    return jsonify({"message":"Parameters recieved, model initiated."})



@app.route('/getAgents', methods=['GET'])
def getAgents():
    if citymodel is None: return
    agent_data = citymodel.get_agent_data()

    print(agent_data)
    return jsonify({'positions': agent_data})

@app.route('/getSemaphores', methods=['GET'])
def getSemaphores():
    if citymodel is None: return
    agent_data = citymodel.get_semaphores()

    print(agent_data)
    return jsonify({'positions': agent_data})

@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global citymodel


    return jsonify({'positions': []})


@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, CityModel
    if request.method == 'GET':
        citymodel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})


if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)
