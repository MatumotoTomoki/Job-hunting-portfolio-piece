// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
#include "EffekseerAlphaBlendType.h"

PRAGMA_DISABLE_DEPRECATION_WARNINGS

void EmptyLinkFunctionForGeneratedCodeEffekseerAlphaBlendType() {}

// ********** Begin Cross Module References ********************************************************
EFFEKSEER_API UEnum* Z_Construct_UEnum_Effekseer_EEffekseerAlphaBlendType();
UPackage* Z_Construct_UPackage__Script_Effekseer();
// ********** End Cross Module References **********************************************************

// ********** Begin Enum EEffekseerAlphaBlendType **************************************************
static FEnumRegistrationInfo Z_Registration_Info_UEnum_EEffekseerAlphaBlendType;
static UEnum* EEffekseerAlphaBlendType_StaticEnum()
{
	if (!Z_Registration_Info_UEnum_EEffekseerAlphaBlendType.OuterSingleton)
	{
		Z_Registration_Info_UEnum_EEffekseerAlphaBlendType.OuterSingleton = GetStaticEnum(Z_Construct_UEnum_Effekseer_EEffekseerAlphaBlendType, (UObject*)Z_Construct_UPackage__Script_Effekseer(), TEXT("EEffekseerAlphaBlendType"));
	}
	return Z_Registration_Info_UEnum_EEffekseerAlphaBlendType.OuterSingleton;
}
template<> EFFEKSEER_API UEnum* StaticEnum<EEffekseerAlphaBlendType>()
{
	return EEffekseerAlphaBlendType_StaticEnum();
}
struct Z_Construct_UEnum_Effekseer_EEffekseerAlphaBlendType_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Enum_MetaDataParams[] = {
		{ "Add.Name", "EEffekseerAlphaBlendType::Add" },
		{ "Blend.Name", "EEffekseerAlphaBlendType::Blend" },
		{ "BlueprintType", "true" },
		{ "ModuleRelativePath", "Public/EffekseerAlphaBlendType.h" },
		{ "Mul.Name", "EEffekseerAlphaBlendType::Mul" },
		{ "Opacity.Name", "EEffekseerAlphaBlendType::Opacity" },
		{ "Sub.Name", "EEffekseerAlphaBlendType::Sub" },
	};
#endif // WITH_METADATA
	static constexpr UECodeGen_Private::FEnumeratorParam Enumerators[] = {
		{ "EEffekseerAlphaBlendType::Opacity", (int64)EEffekseerAlphaBlendType::Opacity },
		{ "EEffekseerAlphaBlendType::Blend", (int64)EEffekseerAlphaBlendType::Blend },
		{ "EEffekseerAlphaBlendType::Add", (int64)EEffekseerAlphaBlendType::Add },
		{ "EEffekseerAlphaBlendType::Sub", (int64)EEffekseerAlphaBlendType::Sub },
		{ "EEffekseerAlphaBlendType::Mul", (int64)EEffekseerAlphaBlendType::Mul },
	};
	static const UECodeGen_Private::FEnumParams EnumParams;
};
const UECodeGen_Private::FEnumParams Z_Construct_UEnum_Effekseer_EEffekseerAlphaBlendType_Statics::EnumParams = {
	(UObject*(*)())Z_Construct_UPackage__Script_Effekseer,
	nullptr,
	"EEffekseerAlphaBlendType",
	"EEffekseerAlphaBlendType",
	Z_Construct_UEnum_Effekseer_EEffekseerAlphaBlendType_Statics::Enumerators,
	RF_Public|RF_Transient|RF_MarkAsNative,
	UE_ARRAY_COUNT(Z_Construct_UEnum_Effekseer_EEffekseerAlphaBlendType_Statics::Enumerators),
	EEnumFlags::None,
	(uint8)UEnum::ECppForm::EnumClass,
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UEnum_Effekseer_EEffekseerAlphaBlendType_Statics::Enum_MetaDataParams), Z_Construct_UEnum_Effekseer_EEffekseerAlphaBlendType_Statics::Enum_MetaDataParams)
};
UEnum* Z_Construct_UEnum_Effekseer_EEffekseerAlphaBlendType()
{
	if (!Z_Registration_Info_UEnum_EEffekseerAlphaBlendType.InnerSingleton)
	{
		UECodeGen_Private::ConstructUEnum(Z_Registration_Info_UEnum_EEffekseerAlphaBlendType.InnerSingleton, Z_Construct_UEnum_Effekseer_EEffekseerAlphaBlendType_Statics::EnumParams);
	}
	return Z_Registration_Info_UEnum_EEffekseerAlphaBlendType.InnerSingleton;
}
// ********** End Enum EEffekseerAlphaBlendType ****************************************************

// ********** Begin Registration *******************************************************************
struct Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerAlphaBlendType_h__Script_Effekseer_Statics
{
	static constexpr FEnumRegisterCompiledInInfo EnumInfo[] = {
		{ EEffekseerAlphaBlendType_StaticEnum, TEXT("EEffekseerAlphaBlendType"), &Z_Registration_Info_UEnum_EEffekseerAlphaBlendType, CONSTRUCT_RELOAD_VERSION_INFO(FEnumReloadVersionInfo, 1220931236U) },
	};
};
static FRegisterCompiledInInfo Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerAlphaBlendType_h__Script_Effekseer_4167540808(TEXT("/Script/Effekseer"),
	nullptr, 0,
	nullptr, 0,
	Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerAlphaBlendType_h__Script_Effekseer_Statics::EnumInfo, UE_ARRAY_COUNT(Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerAlphaBlendType_h__Script_Effekseer_Statics::EnumInfo));
// ********** End Registration *********************************************************************

PRAGMA_ENABLE_DEPRECATION_WARNINGS
