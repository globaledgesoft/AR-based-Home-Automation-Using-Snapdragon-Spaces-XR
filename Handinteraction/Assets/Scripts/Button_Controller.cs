// Importing Necessary Libraries
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using System.Threading.Tasks;
using System;
using System.IO;
using System.Text;
using Amazon.IotData;
using Amazon.IotData.Model;
using TMPro;



// Declaration of Variables
public class Button_Controller : MonoBehaviour     // SampleController
{
    // Public variables to be assigned in the Unity editor
    public Text fanButtonPressText;
    public Text lightButtonPressText;


    // Private variables used in the script
    public Toggle fanButton;
    public Toggle lightButton;
    private string fanStatus;
    private string fanMessage = "off";
    private string lightStatus = "off";
    private string lightMessage;
    private AmazonIotDataClient iotClient;
    private bool isDisabledFan;
    private bool isDisabledLight;
    private float disableTimerFan = 0f;
    private float disableTimerLight = 0f;
    private float disableTime = 2f;


       
    public void Start()
    {
    // Initialization of AWS IoT client
        try 
        {
        // Change AWS Access Key, Secret Key, IoT Endpoint with Your AWS Access Key, Secret Key, IoT Endpoint.
            iotClient = new AmazonIotDataClient(
            "<Use here AWS Access key>",
            "<Use Here AWS Secret Key>",
            "<Use Here AWS IoT Endpoint URL>"

                );
            Debug.Log("AWS IoT client initialized successfully.");
        } 
        catch (Exception e) 
        {
            Debug.LogError("Error initializing AWS IoT client: " + e.Message);
        }

        
    }    

// Time interval 2 sec between each Event
    void Update()
    {
        if (isDisabledFan)
        {
            if (Time.time > disableTimerFan)   /* if time interval grater then 2 sec between two event */
            {
                isDisabledFan = false;  /* fan disable button off */
                fanButton.enabled = true;   /* fan  button enabled */
            }
        }
    
        if (isDisabledLight)  /* if time interval Grater then 2 sec between two event */
        {
            if (Time.time > disableTimerLight)
            {
                isDisabledLight = false; /* light  disable button off */
                lightButton.enabled = true; /* light   button enabled */

            }
        }
    }

    public async void SendData(string topic, string message)
    {
        try
        {
            var request = new PublishRequest
            {
                Topic = topic,
                Payload = new MemoryStream(Encoding.UTF8.GetBytes(message))
            };
            var response = await iotClient.PublishAsync(request);
            Debug.Log($"Message sent to {topic}. Status code: {response.HttpStatusCode}"); 
        
        }
        catch (Exception e)
        {
            Debug.LogError($"Error sending message to {topic}: {e.Message}");
        
        }
    
    }   



    // Fan toggle button handler

    public void OnFanToggle()
    {

        if(fanButton.isOn == true)      /* Fan status is on*/
        {
            fanStatus = "on";  
            // Query send to AWS IOT core     
            fanMessage =  "{\"location\":\"BT-Beacon_room1\",\"devices\":{\"light\":{\"status\": \""+ lightStatus +"\",\"ack\":\"true\",\"err_msg\":\"if any\"},\"fan\":{\"status\":\"on\",\"ack\":\"true\",\"err_msg\":\"if any\"}}}";
            
            DisablFanButton(); 
        }
        else
        {
            fanStatus = "off";  /* fan status is off */
            // Query send to AWS IOT core     
            fanMessage =  "{\"location\":\"BT-Beacon_room1\",\"devices\":{\"light\":{\"status\":\""+ lightStatus + "\",\"ack\":\"true\",\"err_msg\":\"if any\"},\"fan\":{\"status\":\"off\",\"ack\":\"true\",\"err_msg\":\"if any\"}}}";
            DisablFanButton();
        }
        fanButtonPressText.text = fanButton.isOn ? "On":"Off";

        string topic = "<AWS TOPIC>";   /* Give here your AWS Topic for example : "sdk/../../setconfig" */
        SendData(topic, fanMessage);
        
    }

    // Light toggle button handler
    public void OnLightToggle()
    {
    

        if(lightButton.isOn == true)
        {
            lightStatus = "on";  /* Light status is on*/
            // Query send to AWS IOT core     
            lightMessage =  "{\"location\":\"BT-Beacon_room1\",\"devices\":{\"light\":{\"status\":\"on\",\"ack\":\"true\",\"err_msg\":\"if any\"},\"fan\":{\"status\":\""+ fanStatus +"\",\"ack\":\"true\",\"err_msg\":\"if any\"}}}";
            DisablLightButton();
        }
        else
        {
            lightStatus = "off"; /* light  status is off */
            // Query send to AWS IOT core     
            lightMessage =  "{\"location\":\"BT-Beacon_room1\",\"devices\":{\"light\":{\"status\":\"off\",\"ack\":\"true\",\"err_msg\":\"if any\"},\"fan\":{\"status\":\""+ fanStatus + "\",\"ack\":\"true\",\"err_msg\":\"if any\"}}}";
            DisablLightButton();
      
        }
        lightButtonPressText.text = lightStatus;
        string topic = "<AWS TOPIC>";    /* Give here your AWS Topic for example : "sdk/../../setconfig" */
        SendData(topic, lightMessage);
    }

         
    // Disables the fan button for a specified time

    public void DisablFanButton()
    {
        isDisabledFan = true;
        fanButton.enabled = false;
        disableTimerFan = Time.time + disableTime; // Update Time 
    }
        
    
    // Disables the light button for a specified time
    public void DisablLightButton()
    {
        isDisabledLight = true;
        lightButton.enabled = false;
        disableTimerLight = Time.time + disableTime;  // Update Time
    }
    
        
    // Loads the "Menu" scene 
    public void LoadExit()
    {
        SceneManager.LoadScene("Menu");
    }


}


