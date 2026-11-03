// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
#include "EffekseerColorSpaceType.h"

PRAGMA_DISABLE_DEPRECATION_WARNINGS

void EmptyLinkFunctionForGeneratedCodeEffekseerColorSpaceType() {}

// ********** Begin Cross Module References ********************************************************
EFFEKSEER_API UEnum* Z_Construct_UEnum_Effekseer_EEffekseerColorSpaceType();
UPackage* Z_Construct_UPackage__Script_Effekseer();
// ********** End Cross Module References **********************************************************

// ********** Begin Enum EEffekseerColorSpaceType **************************************************
static FEnumRegistrationInfo Z_Registration_Info_UEnum_EEffekseerColorSpaceType;
static UEnum* EEffekseerColorSpaceType_StaticEnum()
{
	if (!Z_Registration_Info_UEnum_EEffekseerColorSpaceType.OuterSingleton)
	{
		Z_Registration_Info_UEnum_EEffekseerColorSpaceType.OuterSingleton = GetStaticEnum(Z_Construct_UEnum_Effekseer_EEffekseerColorSpaceType, (UObject*)Z_Construct_UPackage__Script_Effekseer(), TEXT("EEffekseerColorSpaceType"));
	}
	return Z_Registration_Info_UEnum_EEffekseerColorSpaceType.OuterSingleton;
}
template<> EFFEKSEER_API UEnum* StaticEnum<EEffekseerColorSpaceType>()
{
	return EEffekseerColorSpaceType_StaticEnum();
}
struct Z_Construct_UEnum_Effekseer_EEffekseerColorSpaceType_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Enum_MetaDataParams[] = {
		{ "BlueprintType", "true" },
		{ "Gamma.Name", "EEffekseerColorSpaceType::Gamma" },
		{ "Linear.Name", "EEffekseerColorSpaceType::Linear" },
		{ "ModuleRelativePath", "Public/EffekseerColorSpaceType.h" },
	};
#endif // WITH_METADATA
	static constexpr UECodeGen_Private::FEnumeratorParam Enumerators[] = {
		{ "EEffekseerColorSpaceType::Gamma", (int64)EEffekseerColorSpaceType::Gamma },
		{ "EEffekseerColorSpaceType::Linear", (int64)EEffekseerColorSpaceType::Linear },
	};
	static const UECodeGen_Private::FEnumParams EnumParams;
};
const UECodeGen_Private::FEnumParams Z_Construct_UEnum_Effekseer_EEffekseerColorSpaceType_Statics::EnumParams = {
	(UObject*(*)())Z_Construct_UPackage__Script_Effekseer,
	nullptr,
	"EEffekseerColorSpaceType",
	"EEffekseerColorSpaceType",
	Z_Construct_UEnum_Effekseer_EEffekseerColorSpaceType_Statics::Enumerators,
	RF_Public|RF_Transient|RF_MarkAsNative,
	UE_ARRAY_COUNT(Z_Construct_UEnum_Effekseer_EEffekseerColorSpaceType_Statics::Enumerators),
	EEnumFlags::None,
	(uint8)UEnum::ECppForm::EnumClass,
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UEnum_Effekseer_EEffekseerColorSpaceType_Statics::Enum_MetaDataParams), Z_Construct_UEnum_Effekseer_EEffekseerColorSpaceType_Statics::Enum_MetaDataParams)
};
UEnum* Z_Construct_UEnum_Effekseer_EEffekseerColorSpaceType()
{
	if (!Z_Registration_Info_UEnum_EEffekseerColorSpaceType.InnerSingleton)
	{
		UECodeGen_Private::ConstructUEnum(Z_Registration_Info_UEnum_EEffekseerColorSpaceType.InnerSingleton, Z_Construct_UEnum_Effekseer_EEffekseerColorSpaceType_Statics::EnumParams);
	}
	return Z_Registration_Info_UEnum_EEffekseerColorSpaceType.InnerSingleton;
}
// ********** End Enum EEffekseerColorSpaceType ****************************************************

// ********** Begin Registration *******************************************************************
struct Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerColorSpaceType_h__Script_Effekseer_Statics
{
	static constexpr FEnumRegisterCompiledInInfo EnumInfo[] = {
		{ EEffekseerColorSpaceType_StaticEnum, TEXT("EEffekseerColorSpaceType"), &Z_Registration_Info_UEnum_EEffekseerColorSpaceType, CONSTRUCT_RELOAD_VERSION_INFO(FEnumReloadVersionInfo, 1530459977U) },
	};
};
static FRegisterCompiledInInfo Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerColorSpaceType_h__Script_Effekseer_1761652411(TEXT("/Script/Effekseer"),
	nullptr, 0,
	nullptr, 0,
	Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerColorSpaceType_h__Script_Effekseer_Statics::EnumInfo, UE_ARRAY_COUNT(Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerColorSpaceType_h__Script_Effekseer_Statics::EnumInfo));
// ********** End Registration *********************************************************************

PRAGMA_ENABLE_DEPRECATION_WARNINGS
