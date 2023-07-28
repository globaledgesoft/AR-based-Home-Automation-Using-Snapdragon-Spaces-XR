using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.XR.Interaction.Toolkit.Inputs.Simulation;


namespace QCHT.Samples.Menu
{
    public class StartController : MonoBehaviour
    {
        [SerializeField]
        private SampleSettings startSample;

      
        public void SwitchToScene()
        {
            SceneManager.LoadScene("MainScene");

        }

    }
}

