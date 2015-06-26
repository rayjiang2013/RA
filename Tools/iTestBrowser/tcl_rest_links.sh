#!/bin/sh

TARGET_DIR="/work/mypy/Wrappers/NEW_api_pseudo-code_rest-links"

TEST_TARGET=$TARGET_DIR

if [ "$(ls -A $TEST_TARGET)" ]; then
	echo
	echo "$TEST_TARGET is not empty...  exiting"
	echo
	exit
fi

if [ ! -d $TEST_TARGET ] 
then
	echo
	echo "$TEST_TARGET does not exist...  exiting"
	echo
	exit
fi


for x in AbortTest \
		AddPortGroupToQueue \
		CheckExistenceInTemplate \
		CheckProfileExistenceInLibrary \
		ConfigMuTest \
		ConfigPlayerCpsTest \
		ConfigPlayerDDosTest \
		ConfigPlayerDnsTest \
		ConfigPlayerEmixTest \
		ConfigPlayerFuzzTest \
		ConfigPlayerHttpBandwidthTest \
		ConfigPlayerHttpMaxOpenConnsTest \
		ConvertChassisSlotPort \
		ConvertLibraryAvalancheTestToPlayer \
		ConvertLibraryFuzzTestToPlayer \
		CreateAvalancheTestByJson \
		CreateChassis \
		CreateDNS \
		CreateFuzzTestByJson \
		CreateHost \
		CreateMuTestByJson \
		CreateMuTestFromTemplate \
		CreateNetwork \
		CreatePlayerTestFromTemplate \
		CreateProfile \
		CreateProfileByJson \
		CreateProtocolDNS \
		CreateProtocolHttpRfc6265 \
		CreateProtocolMLD \
		CreateProtocolOpenFlow \
		CreateProtocolSPDYv1 \
		CreateProtocolSPDYv2 \
		CreateProtocolSPDYv3 \
		CreateProtocolTCP \
		CreateProtocolVXLAN \
		CreateQueue \
		CreateSubnet \
		CreateSubnetByJson \
		CreateSubnetFromTemplate \
		CreateTrack \
		CreateTrafficMix \
		CreateUser \
		DeleteChassis \
		DeleteDNS \
		DeleteHost \
		DeleteLibraryProfile \
		DeleteLibraryReport \
		DeleteLibraryTest \
		DeleteMuLibraryTest \
		DeleteNetwork \
		DeleteProtocol \
		DeleteQueue \
		DeleteSubnet \
		DeleteTrack \
		DeleteTrafficMix \
		DeleteUser \
		DownloadTestLogsInLibrary \
		EditUser \
		ExecuteMuTest \
		ExecutePlayerAvalancheTest \
		ExecutePlayerFuzzTest \
		ExecutePlayerTest \
		FormatPlayerSubnetListParamFromSMTest \
		FormatQueueParamFromSMTest \
		GetAllScenariosId \
		GetAllScenariosNum \
		GetAvalancheCPSTest \
		GetAvalancheCPSTests \
		GetAvalancheEmixTest \
		GetAvalancheEmixTests \
		GetAvalancheHttpBandwidthTest \
		GetAvalancheHttpBandwidthTests \
		GetAvalancheTest \
		GetBackupDownload \
		GetBackupInfo \
		GetChassis \
		GetChassisIPFromSMTest \
		GetChassisIPSlotPortFromSMTest \
		GetChassisPortFromSMTest \
		GetChassisPortGroupId \
		GetChassisPortGroupStringId \
		GetChassisSlotFromSMTest \
		GetChassisSlotPortFromSMTest \
		GetChassises \
		GetDNS \
		GetDNSS \
		GetFixturesTrafficMixer \
		GetFuzzTest \
		GetFuzzTestFullLog \
		GetFuzzTestIssues \
		GetFuzzTestLoadStatus \
		GetFuzzTestResult \
		GetFuzzTestRunIdInQueues \
		GetFuzzTestStatus \
		GetFuzzTestVariantLog \
		GetFuzzTestVariantLogPcap \
		GetFuzzTestVariantPcap \
		GetFuzzTests \
		GetHost \
		GetHosts \
		GetLibraryProfiles \
		GetLibraryReports \
		GetLibraryTest \
		GetLibraryTests \
		GetLicenses \
		GetMuLibraryTest \
		GetMuLibraryTests \
		GetNetwork \
		GetNetworks \
		GetPlayerTest \
		GetPlayerTestConfFromLibrary \
		GetPlayerTestNameById \
		GetPlayerTestState \
		GetPlayerTestTemplate \
		GetPlayerTestTimeLine \
		GetPostTestDebug \
		GetPostTestPdf \
		GetPostTestResults \
		GetPostTestRunId \
		GetPostTestRunRef \
		GetPredefinedProtocols \
		GetProtocolConfig \
		GetProtocols \
		GetProtocolsCategory \
		GetProtocolsConfig \
		GetQueue \
		GetQueueId \
		GetQueuePortGroupId \
		GetQueuePortGroupStringId \
		GetQueueRunId \
		GetQueueTestId \
		GetQueueTestStateByName \
		GetQueueTestStatus \
		GetQueues \
		GetSubnet \
		GetSubnetInsertVlanTag \
		GetSubnetIpAddressCount \
		GetSubnetIpAddressEnd \
		GetSubnetIpAddressRange \
		GetSubnetIpAddressStart \
		GetSubnetMacMasqueradeEnable \
		GetSubnetNetMaskBits \
		GetSubnetNetwork \
		GetSubnetOptions \
		GetSubnetRoute \
		GetSubnets \
		GetSuperAdmin \
		GetSystemAbout \
		GetSystemGemStatus \
		GetSystemLiveSupport \
		GetSystemServiceStatus \
		GetSystemVersions \
		GetTestState \
		GetTrack \
		GetTrackDetail \
		GetTracks \
		GetTrafficMix \
		GetTrafficMixes \
		GetUser \
		GetUsers \
		NegativeVerifyQueue \
		PerformBackup \
		RemovePortGroupFromQueue \
		RemoveQueueTest \
		ReplaceAvalancheInterfaceTestConf \
		ReplaceAvalancheSlotTestConf \
		ReplaceAvalancheSubnetTestConf \
		ReplaceAvalancheSwitchDataTestConf \
		ReplaceFuzzInterfaceTestConf \
		ReplaceFuzzSubnetTestConf \
		ReplacePlayerAvalancheCommonTestConf \
		ReplacePlayerFuzzCommonTestConf \
		RestartQueueTest \
		RunFuzzTestByJson \
		RunMuTestByJson \
		RunQueueTestByJson \
		StartTest \
		StopQueueAllTest \
		StopQueueTest \
		StopTest \
		SystemLiveSupportCommand \
		SystemReset \
		UpdateAvalancheTestByJson \
		UpdateDNS \
		UpdateFuzzTestByJson \
		UpdateHost \
		UpdateMuTestByJson \
		UpdateNetwork \
		UpdatePlayerTestNetwork \
		UpdateProtocolTCP \
		UpdateSubnet \
		UpdateSubnetByJson \
		UpdateTrack \
		UpdateTrafficMix \
		VerifyHost \
		VerifyLibraryDNS \
		VerifyLibraryHost \
		VerifyLibraryReport \
		VerifyLibrarySubnet \
		VerifyLibraryTest \
		VerifyMuTestResult \
		VerifyNetwork \
		VerifyPlayerCpsTestConfig \
		VerifyPlayerCpsTestReport \
		VerifyPlayerCpsTestResult \
		VerifyPlayerDDosTestPcap \
		VerifyPlayerDDosTestReport \
		VerifyPlayerDDosTestResult \
		VerifyPlayerDNSTestConfig \
		VerifyPlayerDNSTestPcap \
		VerifyPlayerDNSTestReport \
		VerifyPlayerDNSTestResult \
		VerifyPlayerEmixTestConfig \
		VerifyPlayerEmixTestPcap \
		VerifyPlayerEmixTestReport \
		VerifyPlayerEmixTestResult \
		VerifyPlayerFuzzTestDownload \
		VerifyPlayerFuzzTestReport \
		VerifyPlayerHttpBandwidthTestConfig \
		VerifyPlayerHttpBandwidthTestPcap \
		VerifyPlayerHttpBandwidthTestReport \
		VerifyPlayerHttpBandwidthTestResult \
		VerifyPlayerHttpMaxOpenConnsTestConfig \
		VerifyPlayerHttpMaxOpenConnsTestPcap \
		VerifyPlayerHttpMaxOpenConnsTestReport \
		VerifyPlayerHttpMaxOpenConnsTestResult \
		VerifyPlayerTestPdf \
		VerifyQueue \
		VerifyQueueTestState \
		VerifySubnet \
		http_max_open_head \
		login \
		logout \
		GetApiTestStatistics \
		GetApiTests \
		GetFile \
		GetIPFromName \
		VerifyDNSPcap \
		VerifyEmixPcap \
		VerifyHttpBandwidthPcap \
		VerifyHttpMaxOpenConnsPcap \
		VerifyNetworkPcap \
		VerifySubnetPcap \
		ZipExtract \
		http_max_open_head;

do
    echo $x
	python tcl_rest_links.py $x > $TARGET_DIR/$x.tcl

done

