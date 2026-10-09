// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
#include "VrmSceneCaptureComponent.h"

PRAGMA_DISABLE_DEPRECATION_WARNINGS

void EmptyLinkFunctionForGeneratedCodeVrmSceneCaptureComponent() {}

// ********** Begin Cross Module References ********************************************************
ENGINE_API UClass* Z_Construct_UClass_USceneCaptureComponent2D();
ENGINE_API UClass* Z_Construct_UClass_UTextureRenderTarget2D_NoRegister();
UPackage* Z_Construct_UPackage__Script_VRM4URender();
VRM4URENDER_API UClass* Z_Construct_UClass_UVrmSceneCaptureComponent2D();
VRM4URENDER_API UClass* Z_Construct_UClass_UVrmSceneCaptureComponent2D_NoRegister();
// ********** End Cross Module References **********************************************************

// ********** Begin Class UVrmSceneCaptureComponent2D **********************************************
void UVrmSceneCaptureComponent2D::StaticRegisterNativesUVrmSceneCaptureComponent2D()
{
}
FClassRegistrationInfo Z_Registration_Info_UClass_UVrmSceneCaptureComponent2D;
UClass* UVrmSceneCaptureComponent2D::GetPrivateStaticClass()
{
	using TClass = UVrmSceneCaptureComponent2D;
	if (!Z_Registration_Info_UClass_UVrmSceneCaptureComponent2D.InnerSingleton)
	{
		GetPrivateStaticClassBody(
			StaticPackage(),
			TEXT("VrmSceneCaptureComponent2D"),
			Z_Registration_Info_UClass_UVrmSceneCaptureComponent2D.InnerSingleton,
			StaticRegisterNativesUVrmSceneCaptureComponent2D,
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
	return Z_Registration_Info_UClass_UVrmSceneCaptureComponent2D.InnerSingleton;
}
UClass* Z_Construct_UClass_UVrmSceneCaptureComponent2D_NoRegister()
{
	return UVrmSceneCaptureComponent2D::GetPrivateStaticClass();
}
struct Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Class_MetaDataParams[] = {
		{ "BlueprintSpawnableComponent", "" },
#if !UE_BUILD_SHIPPING
		{ "Comment", "/**\n* Scene Capture component that follows the level editor viewport associated\n* with its world or Player 0's game view, and copies GBuffer-derived and\n* scene-texture data into render targets.\n*/" },
#endif
		{ "HideCategories", "Collision Object Physics SceneComponent Collision Object Physics SceneComponent Mobility Trigger PhysicsVolume" },
		{ "IncludePath", "VrmSceneCaptureComponent.h" },
		{ "ModuleRelativePath", "Public/VrmSceneCaptureComponent.h" },
#if !UE_BUILD_SHIPPING
		{ "ToolTip", "Scene Capture component that follows the level editor viewport associated\nwith its world or Player 0's game view, and copies GBuffer-derived and\nscene-texture data into render targets." },
#endif
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_RT_BaseColor_MetaData[] = {
		{ "Category", "Capture Settings" },
		{ "ModuleRelativePath", "Public/VrmSceneCaptureComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_RT_Normal_MetaData[] = {
		{ "Category", "Capture Settings" },
		{ "ModuleRelativePath", "Public/VrmSceneCaptureComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_RT_MRS_MetaData[] = {
		{ "Category", "Capture Settings" },
#if !UE_BUILD_SHIPPING
		{ "Comment", "/** Metallic / Specular / Roughness (GBufferB) */" },
#endif
		{ "ModuleRelativePath", "Public/VrmSceneCaptureComponent.h" },
#if !UE_BUILD_SHIPPING
		{ "ToolTip", "Metallic / Specular / Roughness (GBufferB)" },
#endif
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_RT_Depth_MetaData[] = {
		{ "Category", "Capture Settings" },
		{ "ModuleRelativePath", "Public/VrmSceneCaptureComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_RT_CustomStencil_MetaData[] = {
		{ "Category", "Capture Settings" },
		{ "ModuleRelativePath", "Public/VrmSceneCaptureComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_RT_CustomDepth_MetaData[] = {
		{ "Category", "Capture Settings" },
		{ "ModuleRelativePath", "Public/VrmSceneCaptureComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_RenderTargetResolutionDivisorX_MetaData[] = {
		{ "Category", "Capture Settings" },
		{ "ModuleRelativePath", "Public/VrmSceneCaptureComponent.h" },
		{ "UIMax", "10.000000" },
		{ "UIMin", "1.000000" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_RenderTargetResolutionDivisorY_MetaData[] = {
		{ "Category", "Capture Settings" },
		{ "ModuleRelativePath", "Public/VrmSceneCaptureComponent.h" },
		{ "UIMax", "10.000000" },
		{ "UIMin", "1.000000" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FObjectPropertyParams NewProp_RT_BaseColor;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_RT_Normal;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_RT_MRS;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_RT_Depth;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_RT_CustomStencil;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_RT_CustomDepth;
	static const UECodeGen_Private::FFloatPropertyParams NewProp_RenderTargetResolutionDivisorX;
	static const UECodeGen_Private::FFloatPropertyParams NewProp_RenderTargetResolutionDivisorY;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static UObject* (*const DependentSingletons[])();
	static constexpr FCppClassTypeInfoStatic StaticCppClassTypeInfo = {
		TCppClassTypeTraits<UVrmSceneCaptureComponent2D>::IsAbstract,
	};
	static const UECodeGen_Private::FClassParams ClassParams;
};
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::NewProp_RT_BaseColor = { "RT_BaseColor", nullptr, (EPropertyFlags)0x0114000000000005, UECodeGen_Private::EPropertyGenFlags::Object | UECodeGen_Private::EPropertyGenFlags::ObjectPtr, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UVrmSceneCaptureComponent2D, RT_BaseColor), Z_Construct_UClass_UTextureRenderTarget2D_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_RT_BaseColor_MetaData), NewProp_RT_BaseColor_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::NewProp_RT_Normal = { "RT_Normal", nullptr, (EPropertyFlags)0x0114000000000005, UECodeGen_Private::EPropertyGenFlags::Object | UECodeGen_Private::EPropertyGenFlags::ObjectPtr, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UVrmSceneCaptureComponent2D, RT_Normal), Z_Construct_UClass_UTextureRenderTarget2D_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_RT_Normal_MetaData), NewProp_RT_Normal_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::NewProp_RT_MRS = { "RT_MRS", nullptr, (EPropertyFlags)0x0114000000000005, UECodeGen_Private::EPropertyGenFlags::Object | UECodeGen_Private::EPropertyGenFlags::ObjectPtr, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UVrmSceneCaptureComponent2D, RT_MRS), Z_Construct_UClass_UTextureRenderTarget2D_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_RT_MRS_MetaData), NewProp_RT_MRS_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::NewProp_RT_Depth = { "RT_Depth", nullptr, (EPropertyFlags)0x0114000000000005, UECodeGen_Private::EPropertyGenFlags::Object | UECodeGen_Private::EPropertyGenFlags::ObjectPtr, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UVrmSceneCaptureComponent2D, RT_Depth), Z_Construct_UClass_UTextureRenderTarget2D_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_RT_Depth_MetaData), NewProp_RT_Depth_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::NewProp_RT_CustomStencil = { "RT_CustomStencil", nullptr, (EPropertyFlags)0x0114000000000005, UECodeGen_Private::EPropertyGenFlags::Object | UECodeGen_Private::EPropertyGenFlags::ObjectPtr, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UVrmSceneCaptureComponent2D, RT_CustomStencil), Z_Construct_UClass_UTextureRenderTarget2D_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_RT_CustomStencil_MetaData), NewProp_RT_CustomStencil_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::NewProp_RT_CustomDepth = { "RT_CustomDepth", nullptr, (EPropertyFlags)0x0114000000000005, UECodeGen_Private::EPropertyGenFlags::Object | UECodeGen_Private::EPropertyGenFlags::ObjectPtr, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UVrmSceneCaptureComponent2D, RT_CustomDepth), Z_Construct_UClass_UTextureRenderTarget2D_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_RT_CustomDepth_MetaData), NewProp_RT_CustomDepth_MetaData) };
const UECodeGen_Private::FFloatPropertyParams Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::NewProp_RenderTargetResolutionDivisorX = { "RenderTargetResolutionDivisorX", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Float, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UVrmSceneCaptureComponent2D, RenderTargetResolutionDivisorX), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_RenderTargetResolutionDivisorX_MetaData), NewProp_RenderTargetResolutionDivisorX_MetaData) };
const UECodeGen_Private::FFloatPropertyParams Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::NewProp_RenderTargetResolutionDivisorY = { "RenderTargetResolutionDivisorY", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Float, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UVrmSceneCaptureComponent2D, RenderTargetResolutionDivisorY), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_RenderTargetResolutionDivisorY_MetaData), NewProp_RenderTargetResolutionDivisorY_MetaData) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::NewProp_RT_BaseColor,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::NewProp_RT_Normal,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::NewProp_RT_MRS,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::NewProp_RT_Depth,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::NewProp_RT_CustomStencil,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::NewProp_RT_CustomDepth,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::NewProp_RenderTargetResolutionDivisorX,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::NewProp_RenderTargetResolutionDivisorY,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::PropPointers) < 2048);
UObject* (*const Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::DependentSingletons[])() = {
	(UObject* (*)())Z_Construct_UClass_USceneCaptureComponent2D,
	(UObject* (*)())Z_Construct_UPackage__Script_VRM4URender,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::DependentSingletons) < 16);
const UECodeGen_Private::FClassParams Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::ClassParams = {
	&UVrmSceneCaptureComponent2D::StaticClass,
	"Engine",
	&StaticCppClassTypeInfo,
	DependentSingletons,
	nullptr,
	Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::PropPointers,
	nullptr,
	UE_ARRAY_COUNT(DependentSingletons),
	0,
	UE_ARRAY_COUNT(Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::PropPointers),
	0,
	0x00B010A4u,
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::Class_MetaDataParams), Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::Class_MetaDataParams)
};
UClass* Z_Construct_UClass_UVrmSceneCaptureComponent2D()
{
	if (!Z_Registration_Info_UClass_UVrmSceneCaptureComponent2D.OuterSingleton)
	{
		UECodeGen_Private::ConstructUClass(Z_Registration_Info_UClass_UVrmSceneCaptureComponent2D.OuterSingleton, Z_Construct_UClass_UVrmSceneCaptureComponent2D_Statics::ClassParams);
	}
	return Z_Registration_Info_UClass_UVrmSceneCaptureComponent2D.OuterSingleton;
}
DEFINE_VTABLE_PTR_HELPER_CTOR(UVrmSceneCaptureComponent2D);
UVrmSceneCaptureComponent2D::~UVrmSceneCaptureComponent2D() {}
// ********** End Class UVrmSceneCaptureComponent2D ************************************************

// ********** Begin Registration *******************************************************************
struct Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_VRM4U_Source_VRM4URender_Public_VrmSceneCaptureComponent_h__Script_VRM4URender_Statics
{
	static constexpr FClassRegisterCompiledInInfo ClassInfo[] = {
		{ Z_Construct_UClass_UVrmSceneCaptureComponent2D, UVrmSceneCaptureComponent2D::StaticClass, TEXT("UVrmSceneCaptureComponent2D"), &Z_Registration_Info_UClass_UVrmSceneCaptureComponent2D, CONSTRUCT_RELOAD_VERSION_INFO(FClassReloadVersionInfo, sizeof(UVrmSceneCaptureComponent2D), 2927614973U) },
	};
};
static FRegisterCompiledInInfo Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_VRM4U_Source_VRM4URender_Public_VrmSceneCaptureComponent_h__Script_VRM4URender_120601971(TEXT("/Script/VRM4URender"),
	Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_VRM4U_Source_VRM4URender_Public_VrmSceneCaptureComponent_h__Script_VRM4URender_Statics::ClassInfo, UE_ARRAY_COUNT(Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_VRM4U_Source_VRM4URender_Public_VrmSceneCaptureComponent_h__Script_VRM4URender_Statics::ClassInfo),
	nullptr, 0,
	nullptr, 0);
// ********** End Registration *********************************************************************

PRAGMA_ENABLE_DEPRECATION_WARNINGS
