// --------------------------------- lda_defintions.h -------------------------------------------
//
//  Include file for Linux LabBrick attenuator defintions
//
// (c) 2020-2021 by Vaunix Technology Corporation, all rights reserved
//
//  JA  Version 1.0 LDA Ethernet Driver Interface Definitions
//-----------------------------------------------------------------------------
#ifdef VNX_ATTEN64_EXPORTS
#define VNX_ATTEN_API __declspec(dllexport)
#else
#define VNX_ATTEN_API __declspec(dllimport) 
#endif

/// ---------- Include headers ----------------

//*****************************************************************************
//
// If building with a C++ compiler, make all of the definitions in this header
// have a C binding.
//
//*****************************************************************************
#ifdef __cplusplus
extern "C"
{
#endif


/// ---------- Macros ----------------
#define MAX_MODELNAME   32
#define MAX_SWVERSION   7
#define MAX_NETBUFF     16

// ----------- Profile Control -----------
#define PROFILE_ONCE	1		// play the profile once
#define PROFILE_REPEAT	2		// play the profile repeatedly
#define PROFILE_OFF	0			// stop the profile


// STATUS ENUM
#define STATUS_OK		0       // 0
#define STATUS_ERROR	1       // 1
#define LDASTATUS 		int

// Hardware type values by device name (used in lda[DeviceId].DevType)
typedef enum
{
    LDA_102=1,      // 1
    LDA_602,        // 2
    LDA_302P_H,     // 3
    LDA_302P_1,     // 4
    LDA_302P_2,     // 5
    LDA_102_75,     // 6
    LDA_102E,       // 7
    LDA_602E,       // 8
    LDA_183,        // 9
    LDA_203,        // 10
    LDA_102EH,      // 11
    LDA_602EH,      // 12
    LDA_602Q,       // 13
    LDA_906V,       // 14
    LDA_133,        // 15
    LDA_5018,       // 16
    LDA_5040,       // 17
    LDA_906V_8,     // 18
    LDA_802EH,      // 19
    LDA_802Q,       // 20
    LDA_802_8,      // 21
    LDA_906V_4,     // 22
    MAX_LDA_DEVICEMODELS
}LDA_DEVICE_MODELS_T;

// LDA Device Response Data Structure
typedef struct
{
  //  Global device variables
  int serialnumber;
  char modelname[MAX_MODELNAME];
  char swversion[MAX_SWVERSION];
  int ipmode;
  char ipaddress[MAX_NETBUFF];
  char netmask[MAX_NETBUFF];
  char gateway[MAX_NETBUFF];
  int minfrequency;
  int maxfrequency;
  int minattenuation;
  int maxattenuation;           // maximum attenuation in .05 db units
  int rf_channel;                  // the current channel number
  int rf_current_frequency;
  int rf_attenuation;                // in .05db units
  int rampstart_attenuation;
  int rampstop_attenuation;
  int ramp_dwelltime;
  int ramp_bidirectional_dwelltime;
  int ramp_idletime;
  int ramp_holdtime;
  int profile_maxlength;
  int profile_count;
  int profile_dwelltime;
  int profile_idletime;
  int profile_index;
} LDADEVICE_DATA_T;

// LDA Device Init
VNX_ATTEN_API void fnLDA_Init(void);

// LDA Test mode
VNX_ATTEN_API void fnLDA_SetTestMode(bool testmode);

// InitDevice
VNX_ATTEN_API LDASTATUS fnLDA_InitDevice(char* deviceip);

// Close the Device Socket
VNX_ATTEN_API LDASTATUS fnLDA_CloseDevice(char* deviceip);

// Device Ready
VNX_ATTEN_API LDASTATUS fnLDA_CheckDeviceReady(char* deviceip);

// Get Model Name
VNX_ATTEN_API LDASTATUS fnLDA_GetModelName(char* deviceip, char *respdata);

// Get Serial Number of the device
VNX_ATTEN_API LDASTATUS fnLDA_GetSerialNumber(char* deviceip, int* respdata);

// Get SW Version of the device
VNX_ATTEN_API LDASTATUS fnLDA_GetSoftwareVersion(char* deviceip, char* respdata);

// Get IP Mode of the device  0 - Static, 1 - DHCP
VNX_ATTEN_API LDASTATUS fnLDA_GetIPMode(char* deviceip, int* respdata);

// Get IP Address of the device
VNX_ATTEN_API LDASTATUS fnLDA_GetIPAddress(char* deviceip, char* respdata);

// Get Netmask of the device
VNX_ATTEN_API LDASTATUS fnLDA_GetNetmask(char* deviceip, char* respdata);

// Get Gateway of the device
VNX_ATTEN_API LDASTATUS fnLDA_GetGateway(char* deviceip, char* respdata);

// Get Current Frequency
VNX_ATTEN_API LDASTATUS fnLDA_GetWorkingFrequency(char* deviceip, int* respdata);

// Get Mininum Frequency
VNX_ATTEN_API LDASTATUS fnLDA_GetMinWorkingFrequency(char* deviceip, int* respdata);

// Get Maximum Frequency
VNX_ATTEN_API LDASTATUS fnLDA_GetMaxWorkingFrequency(char* deviceip, int* respdata);

// Get Channel
VNX_ATTEN_API LDASTATUS fnLDA_GetChannel(char* deviceip, int* respdata);

// Get Max Attenuation
VNX_ATTEN_API LDASTATUS fnLDA_GetMaxAttenuation(char* deviceip, int* respdata);

// Get Min Attenuation
VNX_ATTEN_API LDASTATUS  fnLDA_GetMinAttenuation(char* deviceip, int* respdata);

// Get Attenuation Data
VNX_ATTEN_API LDASTATUS fnLDA_GetAttenuation(char* deviceip, int* respdata);

// Get Ramp Start Data
VNX_ATTEN_API LDASTATUS fnLDA_GetRampStart(char* deviceip, int* respdata);

// Get Ramp End Data
VNX_ATTEN_API LDASTATUS fnLDA_GetRampEnd(char* deviceip, int* respdata);

// Get Dwell Time
VNX_ATTEN_API LDASTATUS fnLDA_GetDwellTime(char* deviceip, int* respdata);
VNX_ATTEN_API LDASTATUS fnLDA_GetDwellTimeTwo(char* deviceip, int* respdata);

// Get Idle Time
VNX_ATTEN_API LDASTATUS fnLDA_GetIdleTime(char* deviceip, int* respdata);

// Get Hold Time
VNX_ATTEN_API LDASTATUS fnLDA_GetHoldTime(char* deviceip, int* respdata);

// Get Profile MaxLength
VNX_ATTEN_API LDASTATUS fnLDA_GetProfileMaxLength(char* deviceip, int* respdata);

// Get Profile Element
VNX_ATTEN_API LDASTATUS fnLDA_GetProfileElement(char* deviceip, int* respdata);

// Get Profile Count
VNX_ATTEN_API LDASTATUS fnLDA_GetProfileCount(char* deviceip, int* respdata);

// Get Profile Dwell Time
VNX_ATTEN_API LDASTATUS fnLDA_GetProfileDwellTime(char* deviceip, int* respdata);

// Get Profile Idle Time
VNX_ATTEN_API LDASTATUS fnLDA_GetProfileIdleTime(char* deviceip, int* respdata);

// Get Profile Index
VNX_ATTEN_API LDASTATUS fnLDA_GetProfileIndex(char* deviceip, int* respdata);

// Set Frequency  --- Frequency in 100KHz Resolution
VNX_ATTEN_API LDASTATUS fnLDA_SetWorkingFrequency(char* deviceip, int frequency);

// Set Channel
VNX_ATTEN_API LDASTATUS fnLDA_SetChannel(char* deviceip, int channel);

// Set Attenuation  -- Attenuation in 0.05db Resolution
VNX_ATTEN_API LDASTATUS fnLDA_SetAttenuation(char* deviceip, int attenuation);

// Set Channel Attenuation -- Attenuation in 0.05db Resolution
VNX_ATTEN_API LDASTATUS fnLDA_SetAttenuationQ(char* deviceip, int attenuation, int channel);

// Set Attenuatuion Step 
VNX_ATTEN_API LDASTATUS fnLDA_SetAttenuationStep(char* deviceip, int attenuationstep);
VNX_ATTEN_API LDASTATUS fnLDA_SetAttenuationStepTwo(char* deviceip, int attenuationstep2);

// Set Ramp Start -- Attenuation in 0.05db Resolution
VNX_ATTEN_API LDASTATUS fnLDA_SetRampStart(char* deviceip, int rampstart);

// Set Ramp End -- Attenuation in 0.05db Resolution
VNX_ATTEN_API LDASTATUS fnLDA_SetRampEnd(char* deviceip, int rampstop);

// Set Dwell Time -- Time in millisecond Resolution
VNX_ATTEN_API LDASTATUS fnLDA_SetDwellTime(char* deviceip, int dwelltime);
VNX_ATTEN_API LDASTATUS fnLDA_SetDwellTimeTwo(char* deviceip, int dwelltime2);

// Set Idle Time -- Time in millisecond Resolution
VNX_ATTEN_API LDASTATUS fnLDA_SetIdleTime(char* deviceip, int idletime);

// Set Hold Time -- Time in millisecond Resolution
VNX_ATTEN_API LDASTATUS fnLDA_SetHoldTime(char* deviceip, int holdtime);

// Set Ramp Direction
VNX_ATTEN_API LDASTATUS fnLDA_SetRampDirection(char* deviceip, bool up);

// Set Ramp Mode
VNX_ATTEN_API LDASTATUS fnLDA_SetRampMode(char* deviceip, bool mode);

// Set Ramp Bidirectional
VNX_ATTEN_API LDASTATUS fnLDA_SetRampBidirectional(char* deviceip, bool bidir_enable);

// Set Profile Element
VNX_ATTEN_API LDASTATUS fnLDA_SetProfileElement(char* deviceip, int index, int attenuation);

// Set Profile Count
VNX_ATTEN_API LDASTATUS fnLDA_SetProfileCount(char* deviceip, int profilecount);

// Set Profile Idle Time
VNX_ATTEN_API LDASTATUS fnLDA_SetProfileIdleTime(char* deviceip, int idletime);

// Set Profile Dwell Time
VNX_ATTEN_API LDASTATUS fnLDA_SetProfileDwellTime(char* deviceip, int dwelltime);

// Set Profile Mode
VNX_ATTEN_API LDASTATUS fnLDA_StartProfile(char* deviceip, int mode);

// Save Setting Callback
VNX_ATTEN_API LDASTATUS fnLDA_SaveSettings(char* deviceip);

// ************** To Be Done
// Set RF On
VNX_ATTEN_API LDASTATUS fnLDA_SetRFOn(char* deviceip, bool on);

// Start Ramp
VNX_ATTEN_API LDASTATUS fnLDA_StartRamp(char* deviceip, bool go);

// Start RampMC
VNX_ATTEN_API LDASTATUS fnLDA_StartRampMC(char* deviceip, int mode, int chmask, bool deferred);

// Start ProfileMC
VNX_ATTEN_API LDASTATUS fnLDA_StartProfileMC(char* deviceip, int mode, int chmask, bool delayed);

//*****************************************************************************
//
// Mark the end of the C bindings section for C++ compilers.
//
//*****************************************************************************
#ifdef __cplusplus
}
#endif