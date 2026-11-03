// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
#include "AnimNotify_PlayEffekseerEffect.h"

PRAGMA_DISABLE_DEPRECATION_WARNINGS

void EmptyLinkFunctionForGeneratedCodeAnimNotify_PlayEffekseerEffect() {}

// ********** Begin Cross Module References ********************************************************
COREUOBJECT_API UScriptStruct* Z_Construct_UScriptStruct_FRotator();
COREUOBJECT_API UScriptStruct* Z_Construct_UScriptStruct_FVector();
EFFEKSEER_API UClass* Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect();
EFFEKSEER_API UClass* Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_NoRegister();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerEffect_NoRegister();
ENGINE_API UClass* Z_Construct_UClass_UAnimNotify();
UPackage* Z_Construct_UPackage__Script_Effekseer();
// ********** End Cross Module References **********************************************************

// ********** Begin Class UAnimNotify_PlayEffekseerEffect ******************************************
void UAnimNotify_PlayEffekseerEffect::StaticRegisterNativesUAnimNotify_PlayEffekseerEffect()
{
}
FClassRegistrationInfo Z_Registration_Info_UClass_UAnimNotify_PlayEffekseerEffect;
UClass* UAnimNotify_PlayEffekseerEffect::GetPrivateStaticClass()
{
	using TClass = UAnimNotify_PlayEffekseerEffect;
	if (!Z_Registration_Info_UClass_UAnimNotify_PlayEffekseerEffect.InnerSingleton)
	{
		GetPrivateStaticClassBody(
			StaticPackage(),
			TEXT("AnimNotify_PlayEffekseerEffect"),
			Z_Registration_Info_UClass_UAnimNotify_PlayEffekseerEffect.InnerSingleton,
			StaticRegisterNativesUAnimNotify_PlayEffekseerEffect,
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
	return Z_Registration_Info_UClass_UAnimNotify_PlayEffekseerEffect.InnerSingleton;
}
UClass* Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_NoRegister()
{
	return UAnimNotify_PlayEffekseerEffect::GetPrivateStaticClass();
}
struct Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Class_MetaDataParams[] = {
#if !UE_BUILD_SHIPPING
		{ "Comment", "/**\n\x09@brief\x09""Animation notify for Effekseer\n\x09@note\n\x09This class is based on Cascade\n*/" },
#endif
		{ "DisplayName", "Play Effekseer Effect" },
		{ "HideCategories", "Object Object" },
		{ "IncludePath", "AnimNotify_PlayEffekseerEffect.h" },
		{ "ModuleRelativePath", "Public/AnimNotify_PlayEffekseerEffect.h" },
#if !UE_BUILD_SHIPPING
		{ "ToolTip", "@brief  Animation notify for Effekseer\n@note\nThis class is based on Cascade" },
#endif
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_EffekseerEffect_MetaData[] = {
		{ "Category", "AnimNotify" },
		{ "DisplayName", "Effekseer Effect" },
		{ "ModuleRelativePath", "Public/AnimNotify_PlayEffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_LocationOffset_MetaData[] = {
		{ "Category", "AnimNotify" },
		{ "ModuleRelativePath", "Public/AnimNotify_PlayEffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_RotationOffset_MetaData[] = {
		{ "Category", "AnimNotify" },
		{ "ModuleRelativePath", "Public/AnimNotify_PlayEffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Attached_MetaData[] = {
		{ "Category", "AnimNotify" },
		{ "ModuleRelativePath", "Public/AnimNotify_PlayEffekseerEffect.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_SocketName_MetaData[] = {
		{ "Category", "AnimNotify" },
		{ "ModuleRelativePath", "Public/AnimNotify_PlayEffekseerEffect.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FObjectPropertyParams NewProp_EffekseerEffect;
	static const UECodeGen_Private::FStructPropertyParams NewProp_LocationOffset;
	static const UECodeGen_Private::FStructPropertyParams NewProp_RotationOffset;
	static void NewProp_Attached_SetBit(void* Obj);
	static const UECodeGen_Private::FBoolPropertyParams NewProp_Attached;
	static const UECodeGen_Private::FNamePropertyParams NewProp_SocketName;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static UObject* (*const DependentSingletons[])();
	static constexpr FCppClassTypeInfoStatic StaticCppClassTypeInfo = {
		TCppClassTypeTraits<UAnimNotify_PlayEffekseerEffect>::IsAbstract,
	};
	static const UECodeGen_Private::FClassParams ClassParams;
};
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::NewProp_EffekseerEffect = { "EffekseerEffect", nullptr, (EPropertyFlags)0x0010000000000011, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UAnimNotify_PlayEffekseerEffect, EffekseerEffect), Z_Construct_UClass_UEffekseerEffect_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_EffekseerEffect_MetaData), NewProp_EffekseerEffect_MetaData) };
const UECodeGen_Private::FStructPropertyParams Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::NewProp_LocationOffset = { "LocationOffset", nullptr, (EPropertyFlags)0x0010000000000011, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UAnimNotify_PlayEffekseerEffect, LocationOffset), Z_Construct_UScriptStruct_FVector, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_LocationOffset_MetaData), NewProp_LocationOffset_MetaData) };
const UECodeGen_Private::FStructPropertyParams Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::NewProp_RotationOffset = { "RotationOffset", nullptr, (EPropertyFlags)0x0010000000000011, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UAnimNotify_PlayEffekseerEffect, RotationOffset), Z_Construct_UScriptStruct_FRotator, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_RotationOffset_MetaData), NewProp_RotationOffset_MetaData) };
void Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::NewProp_Attached_SetBit(void* Obj)
{
	((UAnimNotify_PlayEffekseerEffect*)Obj)->Attached = 1;
}
const UECodeGen_Private::FBoolPropertyParams Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::NewProp_Attached = { "Attached", nullptr, (EPropertyFlags)0x0010000000000011, UECodeGen_Private::EPropertyGenFlags::Bool , RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, sizeof(uint8), sizeof(UAnimNotify_PlayEffekseerEffect), &Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::NewProp_Attached_SetBit, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Attached_MetaData), NewProp_Attached_MetaData) };
const UECodeGen_Private::FNamePropertyParams Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::NewProp_SocketName = { "SocketName", nullptr, (EPropertyFlags)0x0010000000000011, UECodeGen_Private::EPropertyGenFlags::Name, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UAnimNotify_PlayEffekseerEffect, SocketName), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_SocketName_MetaData), NewProp_SocketName_MetaData) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::NewProp_EffekseerEffect,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::NewProp_LocationOffset,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::NewProp_RotationOffset,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::NewProp_Attached,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::NewProp_SocketName,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::PropPointers) < 2048);
UObject* (*const Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::DependentSingletons[])() = {
	(UObject* (*)())Z_Construct_UClass_UAnimNotify,
	(UObject* (*)())Z_Construct_UPackage__Script_Effekseer,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::DependentSingletons) < 16);
const UECodeGen_Private::FClassParams Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::ClassParams = {
	&UAnimNotify_PlayEffekseerEffect::StaticClass,
	nullptr,
	&StaticCppClassTypeInfo,
	DependentSingletons,
	nullptr,
	Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::PropPointers,
	nullptr,
	UE_ARRAY_COUNT(DependentSingletons),
	0,
	UE_ARRAY_COUNT(Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::PropPointers),
	0,
	0x001120A0u,
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::Class_MetaDataParams), Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::Class_MetaDataParams)
};
UClass* Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect()
{
	if (!Z_Registration_Info_UClass_UAnimNotify_PlayEffekseerEffect.OuterSingleton)
	{
		UECodeGen_Private::ConstructUClass(Z_Registration_Info_UClass_UAnimNotify_PlayEffekseerEffect.OuterSingleton, Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect_Statics::ClassParams);
	}
	return Z_Registration_Info_UClass_UAnimNotify_PlayEffekseerEffect.OuterSingleton;
}
DEFINE_VTABLE_PTR_HELPER_CTOR(UAnimNotify_PlayEffekseerEffect);
UAnimNotify_PlayEffekseerEffect::~UAnimNotify_PlayEffekseerEffect() {}
// ********** End Class UAnimNotify_PlayEffekseerEffect ********************************************

// ********** Begin Registration *******************************************************************
struct Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_AnimNotify_PlayEffekseerEffect_h__Script_Effekseer_Statics
{
	static constexpr FClassRegisterCompiledInInfo ClassInfo[] = {
		{ Z_Construct_UClass_UAnimNotify_PlayEffekseerEffect, UAnimNotify_PlayEffekseerEffect::StaticClass, TEXT("UAnimNotify_PlayEffekseerEffect"), &Z_Registration_Info_UClass_UAnimNotify_PlayEffekseerEffect, CONSTRUCT_RELOAD_VERSION_INFO(FClassReloadVersionInfo, sizeof(UAnimNotify_PlayEffekseerEffect), 433514277U) },
	};
};
static FRegisterCompiledInInfo Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_AnimNotify_PlayEffekseerEffect_h__Script_Effekseer_388288784(TEXT("/Script/Effekseer"),
	Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_AnimNotify_PlayEffekseerEffect_h__Script_Effekseer_Statics::ClassInfo, UE_ARRAY_COUNT(Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_AnimNotify_PlayEffekseerEffect_h__Script_Effekseer_Statics::ClassInfo),
	nullptr, 0,
	nullptr, 0);
// ********** End Registration *********************************************************************

PRAGMA_ENABLE_DEPRECATION_WARNINGS
