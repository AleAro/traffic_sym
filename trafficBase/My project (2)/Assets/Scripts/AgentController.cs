// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro. October 2023

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class AgentData
{
    public string id;
    public float x, y, z;

    public AgentData(string id, float x, float y, float z)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}


[Serializable]

public class AgentsData
{
    public List<AgentData> positions;

    public AgentsData() => this.positions = new List<AgentData>();
}

[Serializable]


public class AgentController : MonoBehaviour
{
    string serverUrl = "http://localhost:8585";
    string getAgentsEndpoint = "/getAgents";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    AgentsData agentsData;
    Dictionary<string, GameObject> agents;
    Dictionary<string, Vector3> prevPositions, currPositions;

    bool updated = false, started = false;

    public GameObject agentPrefab, floor;
    public int NAgents;
    private int width = 26, height = 26;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {
        agentsData = new AgentsData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        agents = new Dictionary<string, GameObject>();

        floor.transform.localScale = new Vector3((float)width / 10, 1, (float)height / 10);
        floor.transform.localPosition = new Vector3((float)width / 2 - 0.5f, 0, (float)height / 2 - 0.5f);

        timer = timeToUpdate;

        StartCoroutine(SendConfiguration());
    }

    private void Update()
    {
        if (timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());

        }

        if (updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            foreach (var agent in currPositions)
            {
                Vector3 currentPosition = agent.Value;
                currentPosition.y = 0.2f;

                // Debug.Log($"Update: Agent - {agent.Key} - Position - {currentPosition}");
                // Debug.Log($"Update: Agent - {agent.Key} - Position - {currentPosition.x}, {currentPosition.y}, {currentPosition.z}");
                // Debug.Log($"Current height: {height} - Current width: {width}");

                Vector3 previousPosition = prevPositions[agent.Key];

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                Vector3 direction = currentPosition - interpolated;

                // Debug.Log($"Update: Agent - direction - {direction}");
                agents[agent.Key].transform.localPosition = interpolated;
                if (direction != Vector3.zero) agents[agent.Key].transform.rotation = Quaternion.LookRotation(direction) * Quaternion.Euler(0, -90, 0);
                // rotacion en x y z siempre deben ser cero
                // ponemos en 0 la rotacion en x y z
                Quaternion currentRotation = agents[agent.Key].transform.rotation;
                Vector3 currentEulerAngles = currentRotation.eulerAngles;
                // Establecer la rotación en X y Z a 0, manteniendo la rotación en Y
                Vector3 newEulerAngles = new Vector3(0, currentEulerAngles.y, 0);
                agents[agent.Key].transform.rotation = Quaternion.Euler(newEulerAngles);
                // Debug.Log($"Update: Agent - {agent.Key} - Rotation - {agents[agent.Key].transform.rotation}");
                // Debug.Log($"Update: Agent - {agent.Key} - Rotation - {agents[agent.Key].transform.rotation.x}, {agents[agent.Key].transform.rotation.y}, {agents[agent.Key].transform.rotation.z}");
                // Debug.Log($"Update: Agent - {agent.Key} - Rotation - {agents[agent.Key].transform.rotation.eulerAngles.x}, {agents[agent.Key].transform.rotation.eulerAngles.y}, {agents[agent.Key].transform.rotation.eulerAngles.z}");
            }
        }
    }

    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            StartCoroutine(GetAgentsData());
           
        }
    }

    IEnumerator SendConfiguration()
    {
        WWWForm form = new WWWForm();

        form.AddField("numero_coches_max", NAgents.ToString());

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Configuration upload complete!");
            Debug.Log("Getting Agents positions");

            StartCoroutine(GetAgentsData());
        }
    }

    IEnumerator ActivateAgentWithDelay(GameObject agent, float delay)
    {
        // Espera el tiempo especificado
        yield return new WaitForSeconds(delay);

        // Activa el agente
        agent.SetActive(true);
    }


    IEnumerator GetAgentsData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            AgentsData newData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);
            HashSet<string> receivedAgentIds = new HashSet<string>();

            foreach (AgentData agentData in newData.positions)
            {
                receivedAgentIds.Add(agentData.id);

                Vector3 agentPosition = new Vector3(agentData.x, agentData.z, agentData.y);

                if (!agents.ContainsKey(agentData.id))
                {
                    GameObject newAgent = Instantiate(agentPrefab, agentPosition, Quaternion.identity);
                    // newAgent.transform.rotation = Quaternion.Euler(new Vector3(90, 0, 90));

                    agents.Add(agentData.id, newAgent);
                    prevPositions.Add(agentData.id, agentPosition);
                    // setActive to false
                    agents[agentData.id].SetActive(false);
                    // Inicia la coroutine para activar el agente después del retraso

                }
                else
                {
                    prevPositions[agentData.id] = agents[agentData.id].transform.position;

                }

                currPositions[agentData.id] = agentPosition;
                // si la current position es diferente a la previous position
                if (currPositions[agentData.id] != prevPositions[agentData.id])
                {
                    // if not active setActive to true
                    if (!agents[agentData.id].activeSelf)
                    {
                        StartCoroutine(ActivateAgentWithDelay(agents[agentData.id], timeToUpdate));
                    }
                }
            }

            List<string> keysToRemove = new List<string>();
            foreach (var existingAgent in agents)
            {
                if (!receivedAgentIds.Contains(existingAgent.Key))
                {
                    keysToRemove.Add(existingAgent.Key);
                }
            }

            foreach (var key in keysToRemove)
            {
                Destroy(agents[key]);
                agents.Remove(key);
                prevPositions.Remove(key);
                currPositions.Remove(key);
            }

            updated = true;
            if (!started) started = true;
        }
    }
}