// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
#include "EffekseerCurve.h"
#include "Serialization/ArchiveUObjectFromStructuredArchive.h"

PRAGMA_DISABLE_DEPRECATION_WARNINGS

void EmptyLinkFunctionForGeneratedCodeEffekseerCurve() {}

// ********** Begin Cross Module References ********************************************************
COREUOBJECT_API UClass* Z_Construct_UClass_UObject();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerCurve();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerCurve_NoRegister();
ENGINE_API UClass* Z_Construct_UClass_UAssetImportData_NoRegister();
UPackage* Z_Construct_UPackage__Script_Effekseer();
// ********** End Cross Module References **********************************************************

// ********** Begin Class UEffekseerCurve **********************************************************
void UEffekseerCurve::StaticRegisterNativesUEffekseerCurve()
{
}
FClassRegistrationInfo Z_Registration_Info_UClass_UEffekseerCurve;
UClass* UEffekseerCurve::GetPrivateStaticClass()
{
	using TClass = UEffekseerCurve;
	if (!Z_Registration_Info_UClass_UEffekseerCurve.InnerSingleton)
	{
		GetPrivateStaticClassBody(
			StaticPackage(),
			TEXT("EffekseerCurve"),
			Z_Registration_Info_UClass_UEffekseerCurve.InnerSingleton,
			StaticRegisterNativesUEffekseerCurve,
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
	return Z_Registration_Info_UClass_UEffekseerCurve.InnerSingleton;
}
UClass* Z_Construct_UClass_UEffekseerCurve_NoRegister()
{
	return UEffekseerCurve::GetPrivateStaticClass();
}
struct Z_Construct_UClass_UEffekseerCurve_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Class_MetaDataParams[] = {
		{ "IncludePath", "EffekseerCurve.h" },
		{ "ModuleRelativePath", "Public/EffekseerCurve.h" },
	};
#if WITH_EDITORONLY_DATA
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_AssetImportData_MetaData[] = {
		{ "Category", "ImportSettings" },
		{ "ModuleRelativePath", "Public/EffekseerCurve.h" },
	};
#endif // WITH_EDITORONLY_DATA
#endif // WITH_METADATA
#if WITH_EDITORONLY_DATA
	static const UECodeGen_Private::FObjectPropertyParams NewProp_AssetImportData;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
#endif // WITH_EDITORONLY_DATA
	static UObject* (*const DependentSingletons[])();
	static constexpr FCppClassTypeInfoStatic StaticCppClassTypeInfo = {
		TCppClassTypeTraits<UEffekseerCurve>::IsAbstract,
	};
	static const UECodeGen_Private::FClassParams ClassParams;
};
#if WITH_EDITORONLY_DATA
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerCurve_Statics::NewProp_AssetImportData = { "AssetImportData", nullptr, (EPropertyFlags)0x0010000800020001, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerCurve, AssetImportData), Z_Construct_UClass_UAssetImportData_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_AssetImportData_MetaData), NewProp_AssetImportData_MetaData) };
#endif // WITH_EDITORONLY_DATA
#if WITH_EDITORONLY_DATA
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UClass_UEffekseerCurve_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerCurve_Statics::NewProp_AssetImportData,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerCurve_Statics::PropPointers) < 2048);
#endif // WITH_EDITORONLY_DATA
UObject* (*const Z_Construct_UClass_UEffekseerCurve_Statics::DependentSingletons[])() = {
	(UObject* (*)())Z_Construct_UClass_UObject,
	(UObject* (*)())Z_Construct_UPackage__Script_Effekseer,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerCurve_Statics::DependentSingletons) < 16);
const UECodeGen_Private::FClassParams Z_Construct_UClass_UEffekseerCurve_Statics::ClassParams = {
	&UEffekseerCurve::StaticClass,
	nullptr,
	&StaticCppClassTypeInfo,
	DependentSingletons,
	nullptr,
	IF_WITH_EDITORONLY_DATA(Z_Construct_UClass_UEffekseerCurve_Statics::PropPointers, nullptr),
	nullptr,
	UE_ARRAY_COUNT(DependentSingletons),
	0,
	IF_WITH_EDITORONLY_DATA(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerCurve_Statics::PropPointers), 0),
	0,
	0x001000A0u,
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerCurve_Statics::Class_MetaDataParams), Z_Construct_UClass_UEffekseerCurve_Statics::Class_MetaDataParams)
};
UClass* Z_Construct_UClass_UEffekseerCurve()
{
	if (!Z_Registration_Info_UClass_UEffekseerCurve.OuterSingleton)
	{
		UECodeGen_Private::ConstructUClass(Z_Registration_Info_UClass_UEffekseerCurve.OuterSingleton, Z_Construct_UClass_UEffekseerCurve_Statics::ClassParams);
	}
	return Z_Registration_Info_UClass_UEffekseerCurve.OuterSingleton;
}
UEffekseerCurve::UEffekseerCurve(const FObjectInitializer& ObjectInitializer) : Super(ObjectInitializer) {}
DEFINE_VTABLE_PTR_HELPER_CTOR(UEffekseerCurve);
UEffekseerCurve::~UEffekseerCurve() {}
IMPLEMENT_FSTRUCTUREDARCHIVE_SERIALIZER(UEffekseerCurve)
// ********** End Class UEffekseerCurve ************************************************************

// ********** Begin Registration *******************************************************************
struct Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerCurve_h__Script_Effekseer_Statics
{
	static constexpr FClassRegisterCompiledInInfo ClassInfo[] = {
		{ Z_Construct_UClass_UEffekseerCurve, UEffekseerCurve::StaticClass, TEXT("UEffekseerCurve"), &Z_Registration_Info_UClass_UEffekseerCurve, CONSTRUCT_RELOAD_VERSION_INFO(FClassReloadVersionInfo, sizeof(UEffekseerCurve), 368022492U) },
	};
};
static FRegisterCompiledInInfo Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerCurve_h__Script_Effekseer_4149399306(TEXT("/Script/Effekseer"),
	Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerCurve_h__Script_Effekseer_Statics::ClassInfo, UE_ARRAY_COUNT(Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerCurve_h__Script_Effekseer_Statics::ClassInfo),
	nullptr, 0,
	nullptr, 0);
// ********** End Registration *********************************************************************

PRAGMA_ENABLE_DEPRECATION_WARNINGS
