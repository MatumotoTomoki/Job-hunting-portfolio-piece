// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
#include "EffekseerModel.h"
#include "Serialization/ArchiveUObjectFromStructuredArchive.h"

PRAGMA_DISABLE_DEPRECATION_WARNINGS

void EmptyLinkFunctionForGeneratedCodeEffekseerModel() {}

// ********** Begin Cross Module References ********************************************************
COREUOBJECT_API UClass* Z_Construct_UClass_UObject();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerModel();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerModel_NoRegister();
ENGINE_API UClass* Z_Construct_UClass_UAssetImportData_NoRegister();
ENGINE_API UClass* Z_Construct_UClass_UStaticMesh_NoRegister();
UPackage* Z_Construct_UPackage__Script_Effekseer();
// ********** End Cross Module References **********************************************************

// ********** Begin Class UEffekseerModel **********************************************************
void UEffekseerModel::StaticRegisterNativesUEffekseerModel()
{
}
FClassRegistrationInfo Z_Registration_Info_UClass_UEffekseerModel;
UClass* UEffekseerModel::GetPrivateStaticClass()
{
	using TClass = UEffekseerModel;
	if (!Z_Registration_Info_UClass_UEffekseerModel.InnerSingleton)
	{
		GetPrivateStaticClassBody(
			StaticPackage(),
			TEXT("EffekseerModel"),
			Z_Registration_Info_UClass_UEffekseerModel.InnerSingleton,
			StaticRegisterNativesUEffekseerModel,
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
	return Z_Registration_Info_UClass_UEffekseerModel.InnerSingleton;
}
UClass* Z_Construct_UClass_UEffekseerModel_NoRegister()
{
	return UEffekseerModel::GetPrivateStaticClass();
}
struct Z_Construct_UClass_UEffekseerModel_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Class_MetaDataParams[] = {
		{ "IncludePath", "EffekseerModel.h" },
		{ "ModuleRelativePath", "Public/EffekseerModel.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Mesh_MetaData[] = {
		{ "Category", "Effekseer" },
		{ "ModuleRelativePath", "Public/EffekseerModel.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_AnimationFaceOffsets_MetaData[] = {
		{ "Category", "Effekseer" },
		{ "ModuleRelativePath", "Public/EffekseerModel.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_AnimationFaceCounts_MetaData[] = {
		{ "Category", "Effekseer" },
		{ "ModuleRelativePath", "Public/EffekseerModel.h" },
	};
#if WITH_EDITORONLY_DATA
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_AssetImportData_MetaData[] = {
		{ "Category", "ImportSettings" },
		{ "ModuleRelativePath", "Public/EffekseerModel.h" },
	};
#endif // WITH_EDITORONLY_DATA
#endif // WITH_METADATA
	static const UECodeGen_Private::FObjectPropertyParams NewProp_Mesh;
	static const UECodeGen_Private::FIntPropertyParams NewProp_AnimationFaceOffsets_Inner;
	static const UECodeGen_Private::FArrayPropertyParams NewProp_AnimationFaceOffsets;
	static const UECodeGen_Private::FIntPropertyParams NewProp_AnimationFaceCounts_Inner;
	static const UECodeGen_Private::FArrayPropertyParams NewProp_AnimationFaceCounts;
#if WITH_EDITORONLY_DATA
	static const UECodeGen_Private::FObjectPropertyParams NewProp_AssetImportData;
#endif // WITH_EDITORONLY_DATA
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static UObject* (*const DependentSingletons[])();
	static constexpr FCppClassTypeInfoStatic StaticCppClassTypeInfo = {
		TCppClassTypeTraits<UEffekseerModel>::IsAbstract,
	};
	static const UECodeGen_Private::FClassParams ClassParams;
};
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerModel_Statics::NewProp_Mesh = { "Mesh", nullptr, (EPropertyFlags)0x0010000000000001, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerModel, Mesh), Z_Construct_UClass_UStaticMesh_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Mesh_MetaData), NewProp_Mesh_MetaData) };
const UECodeGen_Private::FIntPropertyParams Z_Construct_UClass_UEffekseerModel_Statics::NewProp_AnimationFaceOffsets_Inner = { "AnimationFaceOffsets", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Int, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FArrayPropertyParams Z_Construct_UClass_UEffekseerModel_Statics::NewProp_AnimationFaceOffsets = { "AnimationFaceOffsets", nullptr, (EPropertyFlags)0x0010000000000001, UECodeGen_Private::EPropertyGenFlags::Array, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerModel, AnimationFaceOffsets), EArrayPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_AnimationFaceOffsets_MetaData), NewProp_AnimationFaceOffsets_MetaData) };
const UECodeGen_Private::FIntPropertyParams Z_Construct_UClass_UEffekseerModel_Statics::NewProp_AnimationFaceCounts_Inner = { "AnimationFaceCounts", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Int, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FArrayPropertyParams Z_Construct_UClass_UEffekseerModel_Statics::NewProp_AnimationFaceCounts = { "AnimationFaceCounts", nullptr, (EPropertyFlags)0x0010000000000001, UECodeGen_Private::EPropertyGenFlags::Array, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerModel, AnimationFaceCounts), EArrayPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_AnimationFaceCounts_MetaData), NewProp_AnimationFaceCounts_MetaData) };
#if WITH_EDITORONLY_DATA
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerModel_Statics::NewProp_AssetImportData = { "AssetImportData", nullptr, (EPropertyFlags)0x0010000800020001, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerModel, AssetImportData), Z_Construct_UClass_UAssetImportData_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_AssetImportData_MetaData), NewProp_AssetImportData_MetaData) };
#endif // WITH_EDITORONLY_DATA
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UClass_UEffekseerModel_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerModel_Statics::NewProp_Mesh,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerModel_Statics::NewProp_AnimationFaceOffsets_Inner,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerModel_Statics::NewProp_AnimationFaceOffsets,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerModel_Statics::NewProp_AnimationFaceCounts_Inner,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerModel_Statics::NewProp_AnimationFaceCounts,
#if WITH_EDITORONLY_DATA
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerModel_Statics::NewProp_AssetImportData,
#endif // WITH_EDITORONLY_DATA
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerModel_Statics::PropPointers) < 2048);
UObject* (*const Z_Construct_UClass_UEffekseerModel_Statics::DependentSingletons[])() = {
	(UObject* (*)())Z_Construct_UClass_UObject,
	(UObject* (*)())Z_Construct_UPackage__Script_Effekseer,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerModel_Statics::DependentSingletons) < 16);
const UECodeGen_Private::FClassParams Z_Construct_UClass_UEffekseerModel_Statics::ClassParams = {
	&UEffekseerModel::StaticClass,
	nullptr,
	&StaticCppClassTypeInfo,
	DependentSingletons,
	nullptr,
	Z_Construct_UClass_UEffekseerModel_Statics::PropPointers,
	nullptr,
	UE_ARRAY_COUNT(DependentSingletons),
	0,
	UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerModel_Statics::PropPointers),
	0,
	0x001000A0u,
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerModel_Statics::Class_MetaDataParams), Z_Construct_UClass_UEffekseerModel_Statics::Class_MetaDataParams)
};
UClass* Z_Construct_UClass_UEffekseerModel()
{
	if (!Z_Registration_Info_UClass_UEffekseerModel.OuterSingleton)
	{
		UECodeGen_Private::ConstructUClass(Z_Registration_Info_UClass_UEffekseerModel.OuterSingleton, Z_Construct_UClass_UEffekseerModel_Statics::ClassParams);
	}
	return Z_Registration_Info_UClass_UEffekseerModel.OuterSingleton;
}
UEffekseerModel::UEffekseerModel(const FObjectInitializer& ObjectInitializer) : Super(ObjectInitializer) {}
DEFINE_VTABLE_PTR_HELPER_CTOR(UEffekseerModel);
UEffekseerModel::~UEffekseerModel() {}
IMPLEMENT_FSTRUCTUREDARCHIVE_SERIALIZER(UEffekseerModel)
// ********** End Class UEffekseerModel ************************************************************

// ********** Begin Registration *******************************************************************
struct Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerModel_h__Script_Effekseer_Statics
{
	static constexpr FClassRegisterCompiledInInfo ClassInfo[] = {
		{ Z_Construct_UClass_UEffekseerModel, UEffekseerModel::StaticClass, TEXT("UEffekseerModel"), &Z_Registration_Info_UClass_UEffekseerModel, CONSTRUCT_RELOAD_VERSION_INFO(FClassReloadVersionInfo, sizeof(UEffekseerModel), 2248846944U) },
	};
};
static FRegisterCompiledInInfo Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerModel_h__Script_Effekseer_396479046(TEXT("/Script/Effekseer"),
	Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerModel_h__Script_Effekseer_Statics::ClassInfo, UE_ARRAY_COUNT(Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerModel_h__Script_Effekseer_Statics::ClassInfo),
	nullptr, 0,
	nullptr, 0);
// ********** End Registration *********************************************************************

PRAGMA_ENABLE_DEPRECATION_WARNINGS
