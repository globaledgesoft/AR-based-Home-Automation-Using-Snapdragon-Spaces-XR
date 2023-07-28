// /******************************************************************************
//  * File: SkinSwitcher.cs
//  * Copyright (c) 2023 Qualcomm Technologies, Inc. and/or its subsidiaries. All rights reserved.
//  *
//  * Confidential and Proprietary - Qualcomm Technologies, Inc.
//  *
//  ******************************************************************************/

using QCHT.Interactions.Core;
using QCHT.Interactions.Hands;
using UnityEngine;

namespace QCHT.Samples.Menu
{
    public class SkinSwitcher : MonoBehaviour
    {
        public void SetLeftSkin(HandSkin skin) => XRHandTrackingManager.LeftHand.HandSkin = skin;
        public void SetRightSkin(HandSkin skin) => XRHandTrackingManager.RightHand.HandSkin = skin;
    }
}