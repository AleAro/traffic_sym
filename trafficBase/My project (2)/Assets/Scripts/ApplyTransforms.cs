/*
Use transformation matrices to modify the vertices of a mesh

Andrés Tarazona
A01023332
*/

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ApplyTransforms : MonoBehaviour
{
    [SerializeField] Vector3 displacement;
    [SerializeField] float angle;
    [SerializeField] AXIS rotationAxis;

    Mesh carMesh;
    Vector3[] baseVertices;
    Vector3[] newVertices;

    [SerializeField] Vector3[] wheelPositions;
    [SerializeField] GameObject wheelPrefab;
    Mesh[] wheelMeshes;
    Vector3[][] wheelVertices;
    Vector3[][] newWheelVertices;
    WheelScript[] wheelScripts;

    public void Initialize()
    {
        carMesh = GetComponentInChildren<MeshFilter>().mesh;
        baseVertices = carMesh.vertices;

        newVertices = new Vector3[baseVertices.Length];
        for (int i = 0; i < baseVertices.Length; i++)
        {
            newVertices[i] = baseVertices[i];
        }

        wheelScripts = new WheelScript[wheelPositions.Length];
        for (int i = 0; i < wheelScripts.Length; i++)
        {
            GameObject temp = Instantiate(wheelPrefab, Vector3.zero, Quaternion.identity);
            wheelScripts[i] = temp.GetComponent<WheelScript>();
            wheelScripts[i].Initialize();
            wheelScripts[i].initial = wheelPositions[i];
        }
    }

    public void DoTransform(Vector3 interpolated, Vector3 direction)
    {

        Matrix4x4 move = HW_Transforms.TranslationMat(interpolated.x, interpolated.y, interpolated.z);
        float angle = Mathf.Atan2(-direction.x, direction.z) * Mathf.Rad2Deg;
        Matrix4x4 rotation_on_y = HW_Transforms.RotateMat(angle, AXIS.Y);
        Matrix4x4 carComposite = move * rotation_on_y;

        for (int i = 0; i < newVertices.Length; i++)
        {
            Vector4 temp = new Vector4(baseVertices[i].x, baseVertices[i].y, baseVertices[i].z, 1);
            newVertices[i] = carComposite * temp;
        }
        carMesh.vertices = newVertices;
        carMesh.RecalculateNormals();

        foreach (WheelScript script in wheelScripts)
        {
            script.ApplyTransform(interpolated, direction, carComposite);
        }
    }
}
