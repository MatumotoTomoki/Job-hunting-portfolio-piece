// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
#include "EffekseerEffect.h"
#include "Serialization/ArchiveUObjectFromStructuredArchive.h"

PRAGMA_DISABLE_DEPRECATION_WARNINGS

void EmptyLinkFunctionForGeneratedCodeEffekseerEffect() {}

// ********** Begin Cross Module References ********************************************************
COREUOBJECT_API UClass* Z_Construct_UClass_UObject();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerCurve_NoRegister();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerEffect();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerEffect_NoRegister();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_NoRegister();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerMaterial_NoRegister();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerModel_NoRegister();
EFFEKSEER_API UClass* Z_Construct_UClass_UEFfekseerProceduralModel_NoRegister();
EFFEKSEER_API UEnum* Z_Construct_UEnum_Effekseer_EEffekseerAlphaBlendType();
EFFEKSEER_API UScriptStruct* Z_Construct_UScriptStruct_FEdgeParameters();
EFFEKSEER_API UScriptStruct* Z_Construct_UScriptStruct_FFalloffParameter();
EFFEKSEER_API UScriptStruct* Z_Construct_UScriptStruct_FFlipbookParameters();
EFFEKSEER_API UScriptStruct* Z_Construct_UScriptStruct_FSoftParticleParameter();
ENGINE_API UClass* Z_Construct_UClass_UAssetImportData_NoRegister();
ENGINE_API UClass* Z_Construct_UClass_UTexture2D_NoRegister();
UPackage* Z_Construct_UPackage__Script_Effekseer();
// ********** End Cross Module References **********************************************************

// ********** Begin ScriptStruct FFlipbookParameters ***********************************************
static FStructRegistrationInfo Z_Registration_Info_UScriptStruct_FFlipbookParameters;
class UScriptStruct* FFlipbookParameters::StaticStruct()
{
	if (!Z_Registration_Info_UScriptStruct_FFlipbookParameters.OuterSingleton)
	{
		Z_Registration_Info_UScriptStruct_FFlipbookParameters.OuterSingleton = GetStaticStruct(Z_Construct_UScriptStruct_FFlipbookParameters, (UObject*)Z_Construct_UPackage__Script_Effekseer(), TEXT("FlipbookParameters"));
	}
	return Z_Registration_Info_UScriptStruct_FFlipbookParameters.OuterSingleton;
}
struct Z_Construct_UScriptStruct_FFlipbookParameters_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Struct_MetaDataParams[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
#endif // WITH_METADATA
	static void* NewStructOps()
	{
		return (UScriptStruct::ICppStructOps*)new UScriptStruct::TCppStructOps<FFlipbookParameters>();
	}
	static const UECodeGen_Private::FStructParams StructParams;
};
const UECodeGen_Private::FStructParams Z_Construct_UScriptStruct_FFlipbookParameters_Statics::StructParams = {
	(UObject* (*)())Z_Construct_UPackage__Script_Effekseer,
	nullptr,
	&NewStructOps,
	"FlipbookParameters",
	nullptr,
	0,
	sizeof(FFlipbookParameters),
	alignof(FFlipbookParameters),
	RF_Public|RF_Transient|RF_MarkAsNative,
	EStructFlags(0x00000001),
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UScriptStruct_FFlipbookParameters_Statics::Struct_MetaDataParams), Z_Construct_UScriptStruct_FFlipbookParameters_Statics::Struct_MetaDataParams)
};
UScriptStruct* Z_Construct_UScriptStruct_FFlipbookParameters()
{
	if (!Z_Registration_Info_UScriptStruct_FFlipbookParameters.InnerSingleton)
	{
		UECodeGen_Private::ConstructUScriptStruct(Z_Registration_Info_UScriptStruct_FFlipbookParameters.InnerSingleton, Z_Construct_UScriptStruct_FFlipbookParameters_Statics::StructParams);
	}
	return Z_Registration_Info_UScriptStruct_FFlipbookParameters.InnerSingleton;
}
// ********** End ScriptStruct FFlipbookParameters *************************************************

// ********** Begin ScriptStruct FEdgeParameters ***************************************************
static FStructRegistrationInfo Z_Registration_Info_UScriptStruct_FEdgeParameters;
class UScriptStruct* FEdgeParameters::StaticStruct()
{
	if (!Z_Registration_Info_UScriptStruct_FEdgeParameters.OuterSingleton)
	{
		Z_Registration_Info_UScriptStruct_FEdgeParameters.OuterSingleton = GetStaticStruct(Z_Construct_UScriptStruct_FEdgeParameters, (UObject*)Z_Construct_UPackage__Script_Effekseer(), TEXT("EdgeParameters"));
	}
	return Z_Registration_Info_UScriptStruct_FEdgeParameters.OuterSingleton;
}
struct Z_Construct_UScriptStruct_FEdgeParameters_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Struct_MetaDataParams[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
#endif // WITH_METADATA
	static void* NewStructOps()
	{
		return (UScriptStruct::ICppStructOps*)new UScriptStruct::TCppStructOps<FEdgeParameters>();
	}
	static const UECodeGen_Private::FStructParams StructParams;
};
const UECodeGen_Private::FStructParams Z_Construct_UScriptStruct_FEdgeParameters_Statics::StructParams = {
	(UObject* (*)())Z_Construct_UPackage__Script_Effekseer,
	nullptr,
	&NewStructOps,
	"EdgeParameters",
	nullptr,
	0,
	sizeof(FEdgeParameters),
	alignof(FEdgeParameters),
	RF_Public|RF_Transient|RF_MarkAsNative,
	EStructFlags(0x00000001),
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UScriptStruct_FEdgeParameters_Statics::Struct_MetaDataParams), Z_Construct_UScriptStruct_FEdgeParameters_Statics::Struct_MetaDataParams)
};
UScriptStruct* Z_Construct_UScriptStruct_FEdgeParameters()
{
	if (!Z_Registration_Info_UScriptStruct_FEdgeParameters.InnerSingleton)
	{
		UECodeGen_Private::ConstructUScriptStruct(Z_Registration_Info_UScriptStruct_FEdgeParameters.InnerSingleton, Z_Construct_UScriptStruct_FEdgeParameters_Statics::StructParams);
	}
	return Z_Registration_Info_UScriptStruct_FEdgeParameters.InnerSingleton;
}
// ********** End ScriptStruct FEdgeParameters *****************************************************

// ********** Begin ScriptStruct FFalloffParameter *************************************************
static FStructRegistrationInfo Z_Registration_Info_UScriptStruct_FFalloffParameter;
class UScriptStruct* FFalloffParameter::StaticStruct()
{
	if (!Z_Registration_Info_UScriptStruct_FFalloffParameter.OuterSingleton)
	{
		Z_Registration_Info_UScriptStruct_FFalloffParameter.OuterSingleton = GetStaticStruct(Z_Construct_UScriptStruct_FFalloffParameter, (UObject*)Z_Construct_UPackage__Script_Effekseer(), TEXT("FalloffParameter"));
	}
	return Z_Registration_Info_UScriptStruct_FFalloffParameter.OuterSingleton;
}
struct Z_Construct_UScriptStruct_FFalloffParameter_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Struct_MetaDataParams[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
#endif // WITH_METADATA
	static void* NewStructOps()
	{
		return (UScriptStruct::ICppStructOps*)new UScriptStruct::TCppStructOps<FFalloffParameter>();
	}
	static const UECodeGen_Private::FStructParams StructParams;
};
const UECodeGen_Private::FStructParams Z_Construct_UScriptStruct_FFalloffParameter_Statics::StructParams = {
	(UObject* (*)())Z_Construct_UPackage__Script_Effekseer,
	nullptr,
	&NewStructOps,
	"FalloffParameter",
	nullptr,
	0,
	sizeof(FFalloffParameter),
	alignof(FFalloffParameter),
	RF_Public|RF_Transient|RF_MarkAsNative,
	EStructFlags(0x00000001),
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UScriptStruct_FFalloffParameter_Statics::Struct_MetaDataParams), Z_Construct_UScriptStruct_FFalloffParameter_Statics::Struct_MetaDataParams)
};
UScriptStruct* Z_Construct_UScriptStruct_FFalloffParameter()
{
	if (!Z_Registration_Info_UScriptStruct_FFalloffParameter.InnerSingleton)
	{
		UECodeGen_Private::ConstructUScriptStruct(Z_Registration_Info_UScriptStruct_FFalloffParameter.InnerSingleton, Z_Construct_UScriptStruct_FFalloffParameter_Statics::StructParams);
	}
	return Z_Registration_Info_UScriptStruct_FFalloffParameter.InnerSingleton;
}
// ********** End ScriptStruct FFalloffParameter ***************************************************

// ********** Begin ScriptStruct FSoftParticleParameter ********************************************
static FStructRegistrationInfo Z_Registration_Info_UScriptStruct_FSoftParticleParameter;
class UScriptStruct* FSoftParticleParameter::StaticStruct()
{
	if (!Z_Registration_Info_UScriptStruct_FSoftParticleParameter.OuterSingleton)
	{
		Z_Registration_Info_UScriptStruct_FSoftParticleParameter.OuterSingleton = GetStaticStruct(Z_Construct_UScriptStruct_FSoftParticleParameter, (UObject*)Z_Construct_UPackage__Script_Effekseer(), TEXT("SoftParticleParameter"));
	}
	return Z_Registration_Info_UScriptStruct_FSoftParticleParameter.OuterSingleton;
}
struct Z_Construct_UScriptStruct_FSoftParticleParameter_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Struct_MetaDataParams[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
#endif // WITH_METADATA
	static void* NewStructOps()
	{
		return (UScriptStruct::ICppStructOps*)new UScriptStruct::TCppStructOps<FSoftParticleParameter>();
	}
	static const UECodeGen_Private::FStructParams StructParams;
};
const UECodeGen_Private::FStructParams Z_Construct_UScriptStruct_FSoftParticleParameter_Statics::StructParams = {
	(UObject* (*)())Z_Construct_UPackage__Script_Effekseer,
	nullptr,
	&NewStructOps,
	"SoftParticleParameter",
	nullptr,
	0,
	sizeof(FSoftParticleParameter),
	alignof(FSoftParticleParameter),
	RF_Public|RF_Transient|RF_MarkAsNative,
	EStructFlags(0x00000001),
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UScriptStruct_FSoftParticleParameter_Statics::Struct_MetaDataParams), Z_Construct_UScriptStruct_FSoftParticleParameter_Statics::Struct_MetaDataParams)
};
UScriptStruct* Z_Construct_UScriptStruct_FSoftParticleParameter()
{
	if (!Z_Registration_Info_UScriptStruct_FSoftParticleParameter.InnerSingleton)
	{
		UECodeGen_Private::ConstructUScriptStruct(Z_Registration_Info_UScriptStruct_FSoftParticleParameter.InnerSingleton, Z_Construct_UScriptStruct_FSoftParticleParameter_Statics::StructParams);
	}
	return Z_Registration_Info_UScriptStruct_FSoftParticleParameter.InnerSingleton;
}
// ********** End ScriptStruct FSoftParticleParameter **********************************************

// ********** Begin Class UEffekseerEffectMaterialParameterHolder **********************************
void UEffekseerEffectMaterialParameterHolder::StaticRegisterNativesUEffekseerEffectMaterialParameterHolder()
{
}
FClassRegistrationInfo Z_Registration_Info_UClass_UEffekseerEffectMaterialParameterHolder;
UClass* UEffekseerEffectMaterialParameterHolder::GetPrivateStaticClass()
{
	using TClass = UEffekseerEffectMaterialParameterHolder;
	if (!Z_Registration_Info_UClass_UEffekseerEffectMaterialParameterHolder.InnerSingleton)
	{
		GetPrivateStaticClassBody(
			StaticPackage(),
			TEXT("EffekseerEffectMaterialParameterHolder"),
			Z_Registration_Info_UClass_UEffekseerEffectMaterialParameterHolder.InnerSingleton,
			StaticRegisterNativesUEffekseerEffectMaterialParameterHolder,
			sizeof(TClass),
			alignof(TClass),
			TClass::StaticClassFlags,
			TClass::StaticClassCastFlags(),
			TClass::StaticConfigName(),
			(UClass::ClassConstructorType)InternalConstructor<TClass>,
			(UClass::ClassVTableHelperCtorCallerType)InternalVTableHelperCtorCaller<TClass>,
			UOBJECT_CPPCLASS_STATICFUNCTIONS_FORCLASS(TClass),
			&TClass::Super::StaticClass,
			&TClass::WithinClass::StaticClass
		);
	}
	return Z_Registration_Info_UClass_UEffekseerEffectMaterialParameterHolder.InnerSingleton;
}
UClass* Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_NoRegister()
{
	return UEffekseerEffectMaterialParameterHolder::GetPrivateStaticClass();
}
struct Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Class_MetaDataParams[] = {
		{ "IncludePath", "EffekseerEffect.h" },
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Texture_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_TextureAddressType_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_AlphaTexture_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_AlphaTextureAddressType_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_UVDistortionTexture_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_UVDistortionTextureAddressType_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_BlendTexture_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_BlendTextureAddress_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_BlendAlphaTexture_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_BlendAlphaTextureAddress_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_BlendUVDistortionTexture_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_BlendUVDistortionTextureAddress_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_FlipbookParams_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_UVDistortionIntensity_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_TextureBlendType_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_BlendUVDistortionIntensity_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_EnableFalloff_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_FalloffParam_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_EmissiveScaling_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_EdgeParams_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_SoftParticleParam_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_AlphaBlend_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_IsDepthTestDisabled_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_IsLighting_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_IsDistorted_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Material_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FObjectPropertyParams NewProp_Texture;
	static const UECodeGen_Private::FIntPropertyParams NewProp_TextureAddressType;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_AlphaTexture;
	static const UECodeGen_Private::FIntPropertyParams NewProp_AlphaTextureAddressType;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_UVDistortionTexture;
	static const UECodeGen_Private::FIntPropertyParams NewProp_UVDistortionTextureAddressType;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_BlendTexture;
	static const UECodeGen_Private::FIntPropertyParams NewProp_BlendTextureAddress;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_BlendAlphaTexture;
	static const UECodeGen_Private::FIntPropertyParams NewProp_BlendAlphaTextureAddress;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_BlendUVDistortionTexture;
	static const UECodeGen_Private::FIntPropertyParams NewProp_BlendUVDistortionTextureAddress;
	static const UECodeGen_Private::FStructPropertyParams NewProp_FlipbookParams;
	static const UECodeGen_Private::FFloatPropertyParams NewProp_UVDistortionIntensity;
	static const UECodeGen_Private::FIntPropertyParams NewProp_TextureBlendType;
	static const UECodeGen_Private::FFloatPropertyParams NewProp_BlendUVDistortionIntensity;
	static void NewProp_EnableFalloff_SetBit(void* Obj);
	static const UECodeGen_Private::FBoolPropertyParams NewProp_EnableFalloff;
	static const UECodeGen_Private::FStructPropertyParams NewProp_FalloffParam;
	static const UECodeGen_Private::FFloatPropertyParams NewProp_EmissiveScaling;
	static const UECodeGen_Private::FStructPropertyParams NewProp_EdgeParams;
	static const UECodeGen_Private::FStructPropertyParams NewProp_SoftParticleParam;
	static const UECodeGen_Private::FBytePropertyParams NewProp_AlphaBlend_Underlying;
	static const UECodeGen_Private::FEnumPropertyParams NewProp_AlphaBlend;
	static void NewProp_IsDepthTestDisabled_SetBit(void* Obj);
	static const UECodeGen_Private::FBoolPropertyParams NewProp_IsDepthTestDisabled;
	static void NewProp_IsLighting_SetBit(void* Obj);
	static const UECodeGen_Private::FBoolPropertyParams NewProp_IsLighting;
	static void NewProp_IsDistorted_SetBit(void* Obj);
	static const UECodeGen_Private::FBoolPropertyParams NewProp_IsDistorted;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_Material;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static UObject* (*const DependentSingletons[])();
	static constexpr FCppClassTypeInfoStatic StaticCppClassTypeInfo = {
		TCppClassTypeTraits<UEffekseerEffectMaterialParameterHolder>::IsAbstract,
	};
	static const UECodeGen_Private::FClassParams ClassParams;
};
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_Texture = { "Texture", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, Texture), Z_Construct_UClass_UTexture2D_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Texture_MetaData), NewProp_Texture_MetaData) };
const UECodeGen_Private::FIntPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_TextureAddressType = { "TextureAddressType", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Int, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, TextureAddressType), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_TextureAddressType_MetaData), NewProp_TextureAddressType_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_AlphaTexture = { "AlphaTexture", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, AlphaTexture), Z_Construct_UClass_UTexture2D_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_AlphaTexture_MetaData), NewProp_AlphaTexture_MetaData) };
const UECodeGen_Private::FIntPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_AlphaTextureAddressType = { "AlphaTextureAddressType", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Int, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, AlphaTextureAddressType), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_AlphaTextureAddressType_MetaData), NewProp_AlphaTextureAddressType_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_UVDistortionTexture = { "UVDistortionTexture", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, UVDistortionTexture), Z_Construct_UClass_UTexture2D_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_UVDistortionTexture_MetaData), NewProp_UVDistortionTexture_MetaData) };
const UECodeGen_Private::FIntPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_UVDistortionTextureAddressType = { "UVDistortionTextureAddressType", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Int, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, UVDistortionTextureAddressType), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_UVDistortionTextureAddressType_MetaData), NewProp_UVDistortionTextureAddressType_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_BlendTexture = { "BlendTexture", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, BlendTexture), Z_Construct_UClass_UTexture2D_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_BlendTexture_MetaData), NewProp_BlendTexture_MetaData) };
const UECodeGen_Private::FIntPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_BlendTextureAddress = { "BlendTextureAddress", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Int, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, BlendTextureAddress), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_BlendTextureAddress_MetaData), NewProp_BlendTextureAddress_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_BlendAlphaTexture = { "BlendAlphaTexture", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, BlendAlphaTexture), Z_Construct_UClass_UTexture2D_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_BlendAlphaTexture_MetaData), NewProp_BlendAlphaTexture_MetaData) };
const UECodeGen_Private::FIntPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_BlendAlphaTextureAddress = { "BlendAlphaTextureAddress", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Int, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, BlendAlphaTextureAddress), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_BlendAlphaTextureAddress_MetaData), NewProp_BlendAlphaTextureAddress_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_BlendUVDistortionTexture = { "BlendUVDistortionTexture", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, BlendUVDistortionTexture), Z_Construct_UClass_UTexture2D_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_BlendUVDistortionTexture_MetaData), NewProp_BlendUVDistortionTexture_MetaData) };
const UECodeGen_Private::FIntPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_BlendUVDistortionTextureAddress = { "BlendUVDistortionTextureAddress", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Int, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, BlendUVDistortionTextureAddress), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_BlendUVDistortionTextureAddress_MetaData), NewProp_BlendUVDistortionTextureAddress_MetaData) };
const UECodeGen_Private::FStructPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_FlipbookParams = { "FlipbookParams", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, FlipbookParams), Z_Construct_UScriptStruct_FFlipbookParameters, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_FlipbookParams_MetaData), NewProp_FlipbookParams_MetaData) }; // 3178640067
const UECodeGen_Private::FFloatPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_UVDistortionIntensity = { "UVDistortionIntensity", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Float, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, UVDistortionIntensity), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_UVDistortionIntensity_MetaData), NewProp_UVDistortionIntensity_MetaData) };
const UECodeGen_Private::FIntPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_TextureBlendType = { "TextureBlendType", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Int, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, TextureBlendType), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_TextureBlendType_MetaData), NewProp_TextureBlendType_MetaData) };
const UECodeGen_Private::FFloatPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_BlendUVDistortionIntensity = { "BlendUVDistortionIntensity", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Float, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, BlendUVDistortionIntensity), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_BlendUVDistortionIntensity_MetaData), NewProp_BlendUVDistortionIntensity_MetaData) };
void Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_EnableFalloff_SetBit(void* Obj)
{
	((UEffekseerEffectMaterialParameterHolder*)Obj)->EnableFalloff = 1;
}
const UECodeGen_Private::FBoolPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_EnableFalloff = { "EnableFalloff", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Bool | UECodeGen_Private::EPropertyGenFlags::NativeBool, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, sizeof(bool), sizeof(UEffekseerEffectMaterialParameterHolder), &Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_EnableFalloff_SetBit, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_EnableFalloff_MetaData), NewProp_EnableFalloff_MetaData) };
const UECodeGen_Private::FStructPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_FalloffParam = { "FalloffParam", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, FalloffParam), Z_Construct_UScriptStruct_FFalloffParameter, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_FalloffParam_MetaData), NewProp_FalloffParam_MetaData) }; // 327557685
const UECodeGen_Private::FFloatPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_EmissiveScaling = { "EmissiveScaling", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Float, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, EmissiveScaling), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_EmissiveScaling_MetaData), NewProp_EmissiveScaling_MetaData) };
const UECodeGen_Private::FStructPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_EdgeParams = { "EdgeParams", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, EdgeParams), Z_Construct_UScriptStruct_FEdgeParameters, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_EdgeParams_MetaData), NewProp_EdgeParams_MetaData) }; // 217274386
const UECodeGen_Private::FStructPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_SoftParticleParam = { "SoftParticleParam", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, SoftParticleParam), Z_Construct_UScriptStruct_FSoftParticleParameter, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_SoftParticleParam_MetaData), NewProp_SoftParticleParam_MetaData) }; // 2076860598
const UECodeGen_Private::FBytePropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_AlphaBlend_Underlying = { "UnderlyingType", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Byte, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, nullptr, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FEnumPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_AlphaBlend = { "AlphaBlend", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Enum, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, AlphaBlend), Z_Construct_UEnum_Effekseer_EEffekseerAlphaBlendType, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_AlphaBlend_MetaData), NewProp_AlphaBlend_MetaData) }; // 1220931236
void Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_IsDepthTestDisabled_SetBit(void* Obj)
{
	((UEffekseerEffectMaterialParameterHolder*)Obj)->IsDepthTestDisabled = 1;
}
const UECodeGen_Private::FBoolPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_IsDepthTestDisabled = { "IsDepthTestDisabled", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Bool | UECodeGen_Private::EPropertyGenFlags::NativeBool, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, sizeof(bool), sizeof(UEffekseerEffectMaterialParameterHolder), &Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_IsDepthTestDisabled_SetBit, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_IsDepthTestDisabled_MetaData), NewProp_IsDepthTestDisabled_MetaData) };
void Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_IsLighting_SetBit(void* Obj)
{
	((UEffekseerEffectMaterialParameterHolder*)Obj)->IsLighting = 1;
}
const UECodeGen_Private::FBoolPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_IsLighting = { "IsLighting", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Bool | UECodeGen_Private::EPropertyGenFlags::NativeBool, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, sizeof(bool), sizeof(UEffekseerEffectMaterialParameterHolder), &Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_IsLighting_SetBit, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_IsLighting_MetaData), NewProp_IsLighting_MetaData) };
void Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_IsDistorted_SetBit(void* Obj)
{
	((UEffekseerEffectMaterialParameterHolder*)Obj)->IsDistorted = 1;
}
const UECodeGen_Private::FBoolPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_IsDistorted = { "IsDistorted", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Bool | UECodeGen_Private::EPropertyGenFlags::NativeBool, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, sizeof(bool), sizeof(UEffekseerEffectMaterialParameterHolder), &Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_IsDistorted_SetBit, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_IsDistorted_MetaData), NewProp_IsDistorted_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_Material = { "Material", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffectMaterialParameterHolder, Material), Z_Construct_UClass_UEffekseerMaterial_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Material_MetaData), NewProp_Material_MetaData) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_Texture,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_TextureAddressType,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_AlphaTexture,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_AlphaTextureAddressType,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_UVDistortionTexture,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_UVDistortionTextureAddressType,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_BlendTexture,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_BlendTextureAddress,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_BlendAlphaTexture,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_BlendAlphaTextureAddress,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_BlendUVDistortionTexture,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_BlendUVDistortionTextureAddress,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_FlipbookParams,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_UVDistortionIntensity,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_TextureBlendType,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_BlendUVDistortionIntensity,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_EnableFalloff,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_FalloffParam,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_EmissiveScaling,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_EdgeParams,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_SoftParticleParam,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_AlphaBlend_Underlying,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_AlphaBlend,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_IsDepthTestDisabled,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_IsLighting,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_IsDistorted,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::NewProp_Material,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::PropPointers) < 2048);
UObject* (*const Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::DependentSingletons[])() = {
	(UObject* (*)())Z_Construct_UClass_UObject,
	(UObject* (*)())Z_Construct_UPackage__Script_Effekseer,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::DependentSingletons) < 16);
const UECodeGen_Private::FClassParams Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::ClassParams = {
	&UEffekseerEffectMaterialParameterHolder::StaticClass,
	nullptr,
	&StaticCppClassTypeInfo,
	DependentSingletons,
	nullptr,
	Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::PropPointers,
	nullptr,
	UE_ARRAY_COUNT(DependentSingletons),
	0,
	UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::PropPointers),
	0,
	0x001000A0u,
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::Class_MetaDataParams), Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::Class_MetaDataParams)
};
UClass* Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder()
{
	if (!Z_Registration_Info_UClass_UEffekseerEffectMaterialParameterHolder.OuterSingleton)
	{
		UECodeGen_Private::ConstructUClass(Z_Registration_Info_UClass_UEffekseerEffectMaterialParameterHolder.OuterSingleton, Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_Statics::ClassParams);
	}
	return Z_Registration_Info_UClass_UEffekseerEffectMaterialParameterHolder.OuterSingleton;
}
UEffekseerEffectMaterialParameterHolder::UEffekseerEffectMaterialParameterHolder(const FObjectInitializer& ObjectInitializer) : Super(ObjectInitializer) {}
DEFINE_VTABLE_PTR_HELPER_CTOR(UEffekseerEffectMaterialParameterHolder);
UEffekseerEffectMaterialParameterHolder::~UEffekseerEffectMaterialParameterHolder() {}
// ********** End Class UEffekseerEffectMaterialParameterHolder ************************************

// ********** Begin Class UEffekseerEffect *********************************************************
void UEffekseerEffect::StaticRegisterNativesUEffekseerEffect()
{
}
FClassRegistrationInfo Z_Registration_Info_UClass_UEffekseerEffect;
UClass* UEffekseerEffect::GetPrivateStaticClass()
{
	using TClass = UEffekseerEffect;
	if (!Z_Registration_Info_UClass_UEffekseerEffect.InnerSingleton)
	{
		GetPrivateStaticClassBody(
			StaticPackage(),
			TEXT("EffekseerEffect"),
			Z_Registration_Info_UClass_UEffekseerEffect.InnerSingleton,
			StaticRegisterNativesUEffekseerEffect,
			sizeof(TClass),
			alignof(TClass),
			TClass::StaticClassFlags,
			TClass::StaticClassCastFlags(),
			TClass::StaticConfigName(),
			(UClass::ClassConstructorType)InternalConstructor<TClass>,
			(UClass::ClassVTableHelperCtorCallerType)InternalVTableHelperCtorCaller<TClass>,
			UOBJECT_CPPCLASS_STATICFUNCTIONS_FORCLASS(TClass),
			&TClass::Super::StaticClass,
			&TClass::WithinClass::StaticClass
		);
	}
	return Z_Registration_Info_UClass_UEffekseerEffect.InnerSingleton;
}
UClass* Z_Construct_UClass_UEffekseerEffect_NoRegister()
{
	return UEffekseerEffect::GetPrivateStaticClass();
}
struct Z_Construct_UClass_UEffekseerEffect_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Class_MetaDataParams[] = {
		{ "IncludePath", "EffekseerEffect.h" },
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_ProceduralModels_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Version_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Scale_MetaData[] = {
		{ "Category", "Effekseer" },
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Name_MetaData[] = {
		{ "Category", "Effekseer" },
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_ColorTextures_MetaData[] = {
		{ "Category", "Effekseer" },
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_DistortionTextures_MetaData[] = {
		{ "Category", "Effekseer" },
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Models_MetaData[] = {
		{ "Category", "Effekseer" },
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Materials_MetaData[] = {
		{ "Category", "Effekseer" },
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Curves_MetaData[] = {
		{ "Category", "Effekseer" },
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_EffekseerMaterials_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
#if WITH_EDITORONLY_DATA
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_AssetImportData_MetaData[] = {
		{ "Category", "ImportSettings" },
		{ "ModuleRelativePath", "Public/EffekseerEffect.h" },
	};
#endif // WITH_EDITORONLY_DATA
#endif // WITH_METADATA
	static const UECodeGen_Private::FObjectPropertyParams NewProp_ProceduralModels_Inner;
	static const UECodeGen_Private::FArrayPropertyParams NewProp_ProceduralModels;
	static const UECodeGen_Private::FIntPropertyParams NewProp_Version;
	static const UECodeGen_Private::FFloatPropertyParams NewProp_Scale;
	static const UECodeGen_Private::FStrPropertyParams NewProp_Name;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_ColorTextures_Inner;
	static const UECodeGen_Private::FArrayPropertyParams NewProp_ColorTextures;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_DistortionTextures_Inner;
	static const UECodeGen_Private::FArrayPropertyParams NewProp_DistortionTextures;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_Models_Inner;
	static const UECodeGen_Private::FArrayPropertyParams NewProp_Models;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_Materials_Inner;
	static const UECodeGen_Private::FArrayPropertyParams NewProp_Materials;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_Curves_Inner;
	static const UECodeGen_Private::FArrayPropertyParams NewProp_Curves;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_EffekseerMaterials_Inner;
	static const UECodeGen_Private::FArrayPropertyParams NewProp_EffekseerMaterials;
#if WITH_EDITORONLY_DATA
	static const UECodeGen_Private::FObjectPropertyParams NewProp_AssetImportData;
#endif // WITH_EDITORONLY_DATA
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static UObject* (*const DependentSingletons[])();
	static constexpr FCppClassTypeInfoStatic StaticCppClassTypeInfo = {
		TCppClassTypeTraits<UEffekseerEffect>::IsAbstract,
	};
	static const UECodeGen_Private::FClassParams ClassParams;
};
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_ProceduralModels_Inner = { "ProceduralModels", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UClass_UEFfekseerProceduralModel_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FArrayPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_ProceduralModels = { "ProceduralModels", nullptr, (EPropertyFlags)0x0040000000002000, UECodeGen_Private::EPropertyGenFlags::Array, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffect, ProceduralModels), EArrayPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_ProceduralModels_MetaData), NewProp_ProceduralModels_MetaData) };
const UECodeGen_Private::FIntPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Version = { "Version", nullptr, (EPropertyFlags)0x0010000000002000, UECodeGen_Private::EPropertyGenFlags::Int, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffect, Version), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Version_MetaData), NewProp_Version_MetaData) };
const UECodeGen_Private::FFloatPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Scale = { "Scale", nullptr, (EPropertyFlags)0x0010000000000001, UECodeGen_Private::EPropertyGenFlags::Float, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffect, Scale), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Scale_MetaData), NewProp_Scale_MetaData) };
const UECodeGen_Private::FStrPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Name = { "Name", nullptr, (EPropertyFlags)0x0010000000020001, UECodeGen_Private::EPropertyGenFlags::Str, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffect, Name), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Name_MetaData), NewProp_Name_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_ColorTextures_Inner = { "ColorTextures", nullptr, (EPropertyFlags)0x0000000000020000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UClass_UTexture2D_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FArrayPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_ColorTextures = { "ColorTextures", nullptr, (EPropertyFlags)0x0010000000020001, UECodeGen_Private::EPropertyGenFlags::Array, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffect, ColorTextures), EArrayPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_ColorTextures_MetaData), NewProp_ColorTextures_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_DistortionTextures_Inner = { "DistortionTextures", nullptr, (EPropertyFlags)0x0000000000020000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UClass_UTexture2D_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FArrayPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_DistortionTextures = { "DistortionTextures", nullptr, (EPropertyFlags)0x0010000000020001, UECodeGen_Private::EPropertyGenFlags::Array, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffect, DistortionTextures), EArrayPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_DistortionTextures_MetaData), NewProp_DistortionTextures_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Models_Inner = { "Models", nullptr, (EPropertyFlags)0x0000000000020000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UClass_UEffekseerModel_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FArrayPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Models = { "Models", nullptr, (EPropertyFlags)0x0010000000020001, UECodeGen_Private::EPropertyGenFlags::Array, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffect, Models), EArrayPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Models_MetaData), NewProp_Models_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Materials_Inner = { "Materials", nullptr, (EPropertyFlags)0x0000000000020000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UClass_UEffekseerMaterial_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FArrayPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Materials = { "Materials", nullptr, (EPropertyFlags)0x0010000000020001, UECodeGen_Private::EPropertyGenFlags::Array, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffect, Materials), EArrayPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Materials_MetaData), NewProp_Materials_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Curves_Inner = { "Curves", nullptr, (EPropertyFlags)0x0000000000020000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UClass_UEffekseerCurve_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FArrayPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Curves = { "Curves", nullptr, (EPropertyFlags)0x0010000000020001, UECodeGen_Private::EPropertyGenFlags::Array, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffect, Curves), EArrayPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Curves_MetaData), NewProp_Curves_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_EffekseerMaterials_Inner = { "EffekseerMaterials", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FArrayPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_EffekseerMaterials = { "EffekseerMaterials", nullptr, (EPropertyFlags)0x0010000000002000, UECodeGen_Private::EPropertyGenFlags::Array, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffect, EffekseerMaterials), EArrayPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_EffekseerMaterials_MetaData), NewProp_EffekseerMaterials_MetaData) };
#if WITH_EDITORONLY_DATA
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_AssetImportData = { "AssetImportData", nullptr, (EPropertyFlags)0x0010000800020001, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEffect, AssetImportData), Z_Construct_UClass_UAssetImportData_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_AssetImportData_MetaData), NewProp_AssetImportData_MetaData) };
#endif // WITH_EDITORONLY_DATA
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UClass_UEffekseerEffect_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_ProceduralModels_Inner,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_ProceduralModels,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Version,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Scale,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Name,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_ColorTextures_Inner,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_ColorTextures,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_DistortionTextures_Inner,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_DistortionTextures,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Models_Inner,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Models,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Materials_Inner,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Materials,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Curves_Inner,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_Curves,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_EffekseerMaterials_Inner,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_EffekseerMaterials,
#if WITH_EDITORONLY_DATA
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEffect_Statics::NewProp_AssetImportData,
#endif // WITH_EDITORONLY_DATA
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerEffect_Statics::PropPointers) < 2048);
UObject* (*const Z_Construct_UClass_UEffekseerEffect_Statics::DependentSingletons[])() = {
	(UObject* (*)())Z_Construct_UClass_UObject,
	(UObject* (*)())Z_Construct_UPackage__Script_Effekseer,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerEffect_Statics::DependentSingletons) < 16);
const UECodeGen_Private::FClassParams Z_Construct_UClass_UEffekseerEffect_Statics::ClassParams = {
	&UEffekseerEffect::StaticClass,
	nullptr,
	&StaticCppClassTypeInfo,
	DependentSingletons,
	nullptr,
	Z_Construct_UClass_UEffekseerEffect_Statics::PropPointers,
	nullptr,
	UE_ARRAY_COUNT(DependentSingletons),
	0,
	UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerEffect_Statics::PropPointers),
	0,
	0x001000A0u,
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerEffect_Statics::Class_MetaDataParams), Z_Construct_UClass_UEffekseerEffect_Statics::Class_MetaDataParams)
};
UClass* Z_Construct_UClass_UEffekseerEffect()
{
	if (!Z_Registration_Info_UClass_UEffekseerEffect.OuterSingleton)
	{
		UECodeGen_Private::ConstructUClass(Z_Registration_Info_UClass_UEffekseerEffect.OuterSingleton, Z_Construct_UClass_UEffekseerEffect_Statics::ClassParams);
	}
	return Z_Registration_Info_UClass_UEffekseerEffect.OuterSingleton;
}
UEffekseerEffect::UEffekseerEffect(const FObjectInitializer& ObjectInitializer) : Super(ObjectInitializer) {}
DEFINE_VTABLE_PTR_HELPER_CTOR(UEffekseerEffect);
UEffekseerEffect::~UEffekseerEffect() {}
IMPLEMENT_FSTRUCTUREDARCHIVE_SERIALIZER(UEffekseerEffect)
// ********** End Class UEffekseerEffect ***********************************************************

// ********** Begin Registration *******************************************************************
struct Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerEffect_h__Script_Effekseer_Statics
{
	static constexpr FStructRegisterCompiledInInfo ScriptStructInfo[] = {
		{ FFlipbookParameters::StaticStruct, Z_Construct_UScriptStruct_FFlipbookParameters_Statics::NewStructOps, TEXT("FlipbookParameters"), &Z_Registration_Info_UScriptStruct_FFlipbookParameters, CONSTRUCT_RELOAD_VERSION_INFO(FStructReloadVersionInfo, sizeof(FFlipbookParameters), 3178640067U) },
		{ FEdgeParameters::StaticStruct, Z_Construct_UScriptStruct_FEdgeParameters_Statics::NewStructOps, TEXT("EdgeParameters"), &Z_Registration_Info_UScriptStruct_FEdgeParameters, CONSTRUCT_RELOAD_VERSION_INFO(FStructReloadVersionInfo, sizeof(FEdgeParameters), 217274386U) },
		{ FFalloffParameter::StaticStruct, Z_Construct_UScriptStruct_FFalloffParameter_Statics::NewStructOps, TEXT("FalloffParameter"), &Z_Registration_Info_UScriptStruct_FFalloffParameter, CONSTRUCT_RELOAD_VERSION_INFO(FStructReloadVersionInfo, sizeof(FFalloffParameter), 327557685U) },
		{ FSoftParticleParameter::StaticStruct, Z_Construct_UScriptStruct_FSoftParticleParameter_Statics::NewStructOps, TEXT("SoftParticleParameter"), &Z_Registration_Info_UScriptStruct_FSoftParticleParameter, CONSTRUCT_RELOAD_VERSION_INFO(FStructReloadVersionInfo, sizeof(FSoftParticleParameter), 2076860598U) },
	};
	static constexpr FClassRegisterCompiledInInfo ClassInfo[] = {
		{ Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder, UEffekseerEffectMaterialParameterHolder::StaticClass, TEXT("UEffekseerEffectMaterialParameterHolder"), &Z_Registration_Info_UClass_UEffekseerEffectMaterialParameterHolder, CONSTRUCT_RELOAD_VERSION_INFO(FClassReloadVersionInfo, sizeof(UEffekseerEffectMaterialParameterHolder), 103622831U) },
		{ Z_Construct_UClass_UEffekseerEffect, UEffekseerEffect::StaticClass, TEXT("UEffekseerEffect"), &Z_Registration_Info_UClass_UEffekseerEffect, CONSTRUCT_RELOAD_VERSION_INFO(FClassReloadVersionInfo, sizeof(UEffekseerEffect), 584561260U) },
	};
};
static FRegisterCompiledInInfo Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerEffect_h__Script_Effekseer_3794463038(TEXT("/Script/Effekseer"),
	Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerEffect_h__Script_Effekseer_Statics::ClassInfo, UE_ARRAY_COUNT(Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerEffect_h__Script_Effekseer_Statics::ClassInfo),
	Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerEffect_h__Script_Effekseer_Statics::ScriptStructInfo, UE_ARRAY_COUNT(Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerEffect_h__Script_Effekseer_Statics::ScriptStructInfo),
	nullptr, 0);
// ********** End Registration *********************************************************************

PRAGMA_ENABLE_DEPRECATION_WARNINGS
