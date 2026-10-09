// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
#include "VrmBoneCheckComponent.h"

PRAGMA_DISABLE_DEPRECATION_WARNINGS

void EmptyLinkFunctionForGeneratedCodeVrmBoneCheckComponent() {}

// ********** Begin Cross Module References ********************************************************
ENGINE_API UClass* Z_Construct_UClass_USceneComponent();
UPackage* Z_Construct_UPackage__Script_VRM4U();
VRM4U_API UClass* Z_Construct_UClass_UVrmBoneCheckComponent();
VRM4U_API UClass* Z_Construct_UClass_UVrmBoneCheckComponent_NoRegister();
VRM4U_API UFunction* Z_Construct_UDelegateFunction_UVrmBoneCheckComponent_VrmBoneCheckDelegate__DelegateSignature();
// ********** End Cross Module References **********************************************************

// ********** Begin Delegate FVrmBoneCheckDelegate *************************************************
struct Z_Construct_UDelegateFunction_UVrmBoneCheckComponent_VrmBoneCheckDelegate__DelegateSignature_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "ModuleRelativePath", "Public/VrmBoneCheckComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FDelegateFunctionParams FuncParams;
};
const UECodeGen_Private::FDelegateFunctionParams Z_Construct_UDelegateFunction_UVrmBoneCheckComponent_VrmBoneCheckDelegate__DelegateSignature_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UVrmBoneCheckComponent, nullptr, "VrmBoneCheckDelegate__DelegateSignature", nullptr, 0, 0, RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x00130000, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UDelegateFunction_UVrmBoneCheckComponent_VrmBoneCheckDelegate__DelegateSignature_Statics::Function_MetaDataParams), Z_Construct_UDelegateFunction_UVrmBoneCheckComponent_VrmBoneCheckDelegate__DelegateSignature_Statics::Function_MetaDataParams)},  };
UFunction* Z_Construct_UDelegateFunction_UVrmBoneCheckComponent_VrmBoneCheckDelegate__DelegateSignature()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUDelegateFunction(&ReturnFunction, Z_Construct_UDelegateFunction_UVrmBoneCheckComponent_VrmBoneCheckDelegate__DelegateSignature_Statics::FuncParams);
	}
	return ReturnFunction;
}
void UVrmBoneCheckComponent::FVrmBoneCheckDelegate_DelegateWrapper(const FMulticastScriptDelegate& VrmBoneCheckDelegate)
{
	VrmBoneCheckDelegate.ProcessMulticastDelegate<UObject>(NULL);
}
// ********** End Delegate FVrmBoneCheckDelegate ***************************************************

// ********** Begin Class UVrmBoneCheckComponent ***************************************************
void UVrmBoneCheckComponent::StaticRegisterNativesUVrmBoneCheckComponent()
{
}
FClassRegistrationInfo Z_Registration_Info_UClass_UVrmBoneCheckComponent;
UClass* UVrmBoneCheckComponent::GetPrivateStaticClass()
{
	using TClass = UVrmBoneCheckComponent;
	if (!Z_Registration_Info_UClass_UVrmBoneCheckComponent.InnerSingleton)
	{
		GetPrivateStaticClassBody(
			StaticPackage(),
			TEXT("VrmBoneCheckComponent"),
			Z_Registration_Info_UClass_UVrmBoneCheckComponent.InnerSingleton,
			StaticRegisterNativesUVrmBoneCheckComponent,
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
	return Z_Registration_Info_UClass_UVrmBoneCheckComponent.InnerSingleton;
}
UClass* Z_Construct_UClass_UVrmBoneCheckComponent_NoRegister()
{
	return UVrmBoneCheckComponent::GetPrivateStaticClass();
}
struct Z_Construct_UClass_UVrmBoneCheckComponent_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Class_MetaDataParams[] = {
		{ "BlueprintSpawnableComponent", "" },
		{ "BlueprintType", "true" },
		{ "HideCategories", "Trigger PhysicsVolume" },
		{ "IncludePath", "VrmBoneCheckComponent.h" },
		{ "IsBlueprintBase", "true" },
		{ "ModuleRelativePath", "Public/VrmBoneCheckComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_OnBoneTransform_MetaData[] = {
		{ "ModuleRelativePath", "Public/VrmBoneCheckComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FMulticastDelegatePropertyParams NewProp_OnBoneTransform;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static UObject* (*const DependentSingletons[])();
	static constexpr FClassFunctionLinkInfo FuncInfo[] = {
		{ &Z_Construct_UDelegateFunction_UVrmBoneCheckComponent_VrmBoneCheckDelegate__DelegateSignature, "VrmBoneCheckDelegate__DelegateSignature" }, // 1919884095
	};
	static_assert(UE_ARRAY_COUNT(FuncInfo) < 2048);
	static constexpr FCppClassTypeInfoStatic StaticCppClassTypeInfo = {
		TCppClassTypeTraits<UVrmBoneCheckComponent>::IsAbstract,
	};
	static const UECodeGen_Private::FClassParams ClassParams;
};
const UECodeGen_Private::FMulticastDelegatePropertyParams Z_Construct_UClass_UVrmBoneCheckComponent_Statics::NewProp_OnBoneTransform = { "OnBoneTransform", nullptr, (EPropertyFlags)0x0010000010080000, UECodeGen_Private::EPropertyGenFlags::InlineMulticastDelegate, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UVrmBoneCheckComponent, OnBoneTransform), Z_Construct_UDelegateFunction_UVrmBoneCheckComponent_VrmBoneCheckDelegate__DelegateSignature, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_OnBoneTransform_MetaData), NewProp_OnBoneTransform_MetaData) }; // 1919884095
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UClass_UVrmBoneCheckComponent_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UVrmBoneCheckComponent_Statics::NewProp_OnBoneTransform,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UVrmBoneCheckComponent_Statics::PropPointers) < 2048);
UObject* (*const Z_Construct_UClass_UVrmBoneCheckComponent_Statics::DependentSingletons[])() = {
	(UObject* (*)())Z_Construct_UClass_USceneComponent,
	(UObject* (*)())Z_Construct_UPackage__Script_VRM4U,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UVrmBoneCheckComponent_Statics::DependentSingletons) < 16);
const UECodeGen_Private::FClassParams Z_Construct_UClass_UVrmBoneCheckComponent_Statics::ClassParams = {
	&UVrmBoneCheckComponent::StaticClass,
	"Engine",
	&StaticCppClassTypeInfo,
	DependentSingletons,
	FuncInfo,
	Z_Construct_UClass_UVrmBoneCheckComponent_Statics::PropPointers,
	nullptr,
	UE_ARRAY_COUNT(DependentSingletons),
	UE_ARRAY_COUNT(FuncInfo),
	UE_ARRAY_COUNT(Z_Construct_UClass_UVrmBoneCheckComponent_Statics::PropPointers),
	0,
	0x00B000A4u,
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UClass_UVrmBoneCheckComponent_Statics::Class_MetaDataParams), Z_Construct_UClass_UVrmBoneCheckComponent_Statics::Class_MetaDataParams)
};
UClass* Z_Construct_UClass_UVrmBoneCheckComponent()
{
	if (!Z_Registration_Info_UClass_UVrmBoneCheckComponent.OuterSingleton)
	{
		UECodeGen_Private::ConstructUClass(Z_Registration_Info_UClass_UVrmBoneCheckComponent.OuterSingleton, Z_Construct_UClass_UVrmBoneCheckComponent_Statics::ClassParams);
	}
	return Z_Registration_Info_UClass_UVrmBoneCheckComponent.OuterSingleton;
}
DEFINE_VTABLE_PTR_HELPER_CTOR(UVrmBoneCheckComponent);
UVrmBoneCheckComponent::~UVrmBoneCheckComponent() {}
// ********** End Class UVrmBoneCheckComponent *****************************************************

// ********** Begin Registration *******************************************************************
struct Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_VRM4U_Source_VRM4U_Public_VrmBoneCheckComponent_h__Script_VRM4U_Statics
{
	static constexpr FClassRegisterCompiledInInfo ClassInfo[] = {
		{ Z_Construct_UClass_UVrmBoneCheckComponent, UVrmBoneCheckComponent::StaticClass, TEXT("UVrmBoneCheckComponent"), &Z_Registration_Info_UClass_UVrmBoneCheckComponent, CONSTRUCT_RELOAD_VERSION_INFO(FClassReloadVersionInfo, sizeof(UVrmBoneCheckComponent), 3516339244U) },
	};
};
static FRegisterCompiledInInfo Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_VRM4U_Source_VRM4U_Public_VrmBoneCheckComponent_h__Script_VRM4U_428794797(TEXT("/Script/VRM4U"),
	Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_VRM4U_Source_VRM4U_Public_VrmBoneCheckComponent_h__Script_VRM4U_Statics::ClassInfo, UE_ARRAY_COUNT(Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_VRM4U_Source_VRM4U_Public_VrmBoneCheckComponent_h__Script_VRM4U_Statics::ClassInfo),
	nullptr, 0,
	nullptr, 0);
// ********** End Registration *********************************************************************

PRAGMA_ENABLE_DEPRECATION_WARNINGS
