using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class OnClick : MonoBehaviour
{
   public TextMeshProUGUI text;

   public void OnButtonClick()
   {
        text.text = "Hello";
   }
}
