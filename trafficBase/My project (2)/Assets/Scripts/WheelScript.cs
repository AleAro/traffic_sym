using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class WheelScript : MonoBehaviour
{

    public Vector3 initial;
    float angle = 12f;
    Vector3[] wheelVertices;
    Vector3[] newWheelVertices;
    Mesh wheelMesh;
    public void Initialize()
    {
        wheelMesh = GetComponentInChildren<MeshFilter>().mesh;
        wheelVertices = wheelMesh.vertices;
        newWheelVertices = new Vector3[wheelVertices.Length];
        for (int i = 0; i < wheelVertices.Length; i++)
        {
            newWheelVertices[i] = wheelVertices[i];
        }
    }
    public void ApplyTransform(Vector3 interpolated, Vector3 direction, Matrix4x4 carComposite)
    {
        Matrix4x4 rotate = HW_Transforms.RotateMat(angle * Time.time, AXIS.X);
        Matrix4x4 wheelMove = HW_Transforms.TranslationMat(initial.x, initial.y, initial.z);

        for (int i = 0; i < newWheelVertices.Length; i++)
        {
            Vector4 temp = new Vector4(wheelVertices[i].x, wheelVertices[i].y, wheelVertices[i].z, 1);
            newWheelVertices[i] = carComposite * wheelMove * rotate * temp;
        }

        wheelMesh.vertices = newWheelVertices;
        wheelMesh.RecalculateNormals();
    }
}
