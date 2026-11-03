// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
#include "EffekseerHandle.h"

PRAGMA_DISABLE_DEPRECATION_WARNINGS

void EmptyLinkFunctionForGeneratedCodeEffekseerHandle() {}

// ********** Begin Cross Module References ********************************************************
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerEffect_NoRegister();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerSystemComponent_NoRegister();
EFFEKSEER_API UScriptStruct* Z_Construct_UScriptStruct_FEffekseerHandle();
UPackage* Z_Construct_UPackage__Script_Effekseer();
// ********** End Cross Module References **********************************************************

// ********** Begin ScriptStruct FEffekseerHandle **************************************************
static FStructRegistrationInfo Z_Registration_Info_UScriptStruct_FEffekseerHandle;
class UScriptStruct* FEffekseerHandle::StaticStruct()
{
	if (!Z_Registration_Info_UScriptStruct_FEffekseerHandle.OuterSingleton)
	{
		Z_Registration_Info_UScriptStruct_FEffekseerHandle.OuterSingleton = GetStaticStruct(Z_Construct_UScriptStruct_FEffekseerHandle, (UObject*)Z_Construct_UPackage__Script_Effekseer(), TEXT("EffekseerHandle"));
	}
	return Z_Registration_Info_UScriptStruct_FEffekseerHandle.OuterSingleton;
}
struct Z_Construct_UScriptStruct_FEffekseerHandle_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Struct_MetaDataParams[] = {
		{ "BlueprintType", "true" },
		{ "ModuleRelativePath", "Public/EffekseerHandle.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Effect_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerHandle.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_System_MetaData[] = {
		{ "Category", "Effekseer" },
		{ "EditInline", "true" },
		{ "ModuleRelativePath", "Public/EffekseerHandle.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_ID_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerHandle.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FObjectPropertyParams NewProp_Effect;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_System;
	static const UECodeGen_Private::FIntPropertyParams NewProp_ID;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static void* NewStructOps()
	{
		return (UScriptStruct::ICppStructOps*)new UScriptStruct::TCppStructOps<FEffekseerHandle>();
	}
	static const UECodeGen_Private::FStructParams StructParams;
};
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UScriptStruct_FEffekseerHandle_Statics::NewProp_Effect = { "Effect", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(FEffekseerHandle, Effect), Z_Construct_UClass_UEffekseerEffect_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Effect_MetaData), NewProp_Effect_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UScriptStruct_FEffekseerHandle_Statics::NewProp_System = { "System", nullptr, (EPropertyFlags)0x001000000008000d, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(FEffekseerHandle, System), Z_Construct_UClass_UEffekseerSystemComponent_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_System_MetaData), NewProp_System_MetaData) };
const UECodeGen_Private::FIntPropertyParams Z_Construct_UScriptStruct_FEffekseerHandle_Statics::NewProp_ID = { "ID", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Int, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(FEffekseerHandle, ID), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_ID_MetaData), NewProp_ID_MetaData) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UScriptStruct_FEffekseerHandle_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UScriptStruct_FEffekseerHandle_Statics::NewProp_Effect,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UScriptStruct_FEffekseerHandle_Statics::NewProp_System,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UScriptStruct_FEffekseerHandle_Statics::NewProp_ID,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UScriptStruct_FEffekseerHandle_Statics::PropPointers) < 2048);
const UECodeGen_Private::FStructParams Z_Construct_UScriptStruct_FEffekseerHandle_Statics::StructParams = {
	(UObject* (*)())Z_Construct_UPackage__Script_Effekseer,
	nullptr,
	&NewStructOps,
	"EffekseerHandle",
	Z_Construct_UScriptStruct_FEffekseerHandle_Statics::PropPointers,
	UE_ARRAY_COUNT(Z_Construct_UScriptStruct_FEffekseerHandle_Statics::PropPointers),
	sizeof(FEffekseerHandle),
	alignof(FEffekseerHandle),
	RF_Public|RF_Transient|RF_MarkAsNative,
	EStructFlags(0x00000205),
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UScriptStruct_FEffekseerHandle_Statics::Struct_MetaDataParams), Z_Construct_UScriptStruct_FEffekseerHandle_Statics::Struct_MetaDataParams)
};
UScriptStruct* Z_Construct_UScriptStruct_FEffekseerHandle()
{
	if (!Z_Registration_Info_UScriptStruct_FEffekseerHandle.InnerSingleton)
	{
		UECodeGen_Private::ConstructUScriptStruct(Z_Registration_Info_UScriptStruct_FEffekseerHandle.InnerSingleton, Z_Construct_UScriptStruct_FEffekseerHandle_Statics::StructParams);
	}
	return Z_Registration_Info_UScriptStruct_FEffekseerHandle.InnerSingleton;
}
// ********** End ScriptStruct FEffekseerHandle ****************************************************

// ********** Begin Registration *******************************************************************
struct Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerHandle_h__Script_Effekseer_Statics
{
	static constexpr FStructRegisterCompiledInInfo ScriptStructInfo[] = {
		{ FEffekseerHandle::StaticStruct, Z_Construct_UScriptStruct_FEffekseerHandle_Statics::NewStructOps, TEXT("EffekseerHandle"), &Z_Registration_Info_UScriptStruct_FEffekseerHandle, CONSTRUCT_RELOAD_VERSION_INFO(FStructReloadVersionInfo, sizeof(FEffekseerHandle), 4118386477U) },
	};
};
static FRegisterCompiledInInfo Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerHandle_h__Script_Effekseer_2605249981(TEXT("/Script/Effekseer"),
	nullptr, 0,
	Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerHandle_h__Script_Effekseer_Statics::ScriptStructInfo, UE_ARRAY_COUNT(Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerHandle_h__Script_Effekseer_Statics::ScriptStructInfo),
	nullptr, 0);
// ********** End Registration *********************************************************************

PRAGMA_ENABLE_DEPRECATION_WARNINGS
