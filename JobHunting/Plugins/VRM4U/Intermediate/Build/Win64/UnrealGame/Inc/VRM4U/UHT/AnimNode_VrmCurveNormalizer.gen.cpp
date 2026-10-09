// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
#include "AnimNode_VrmCurveNormalizer.h"
#include "Animation/AnimNodeBase.h"

PRAGMA_DISABLE_DEPRECATION_WARNINGS

void EmptyLinkFunctionForGeneratedCodeAnimNode_VrmCurveNormalizer() {}

// ********** Begin Cross Module References ********************************************************
ENGINE_API UScriptStruct* Z_Construct_UScriptStruct_FAnimNode_Base();
ENGINE_API UScriptStruct* Z_Construct_UScriptStruct_FPoseLink();
UPackage* Z_Construct_UPackage__Script_VRM4U();
VRM4U_API UScriptStruct* Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer();
VRM4U_API UScriptStruct* Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup();
// ********** End Cross Module References **********************************************************

// ********** Begin ScriptStruct FVrmCurveNormalizationGroup ***************************************
static FStructRegistrationInfo Z_Registration_Info_UScriptStruct_FVrmCurveNormalizationGroup;
class UScriptStruct* FVrmCurveNormalizationGroup::StaticStruct()
{
	if (!Z_Registration_Info_UScriptStruct_FVrmCurveNormalizationGroup.OuterSingleton)
	{
		Z_Registration_Info_UScriptStruct_FVrmCurveNormalizationGroup.OuterSingleton = GetStaticStruct(Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup, (UObject*)Z_Construct_UPackage__Script_VRM4U(), TEXT("VrmCurveNormalizationGroup"));
	}
	return Z_Registration_Info_UScriptStruct_FVrmCurveNormalizationGroup.OuterSingleton;
}
struct Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Struct_MetaDataParams[] = {
		{ "BlueprintType", "true" },
		{ "ModuleRelativePath", "Public/AnimNode_VrmCurveNormalizer.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_CurveNames_MetaData[] = {
		{ "Category", "Curve Normalization" },
#if !UE_BUILD_SHIPPING
		{ "Comment", "/** Curves that share the same value budget. Their relative balance is preserved. */" },
#endif
		{ "ModuleRelativePath", "Public/AnimNode_VrmCurveNormalizer.h" },
#if !UE_BUILD_SHIPPING
		{ "ToolTip", "Curves that share the same value budget. Their relative balance is preserved." },
#endif
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_MaximumCombinedValue_MetaData[] = {
		{ "Category", "Curve Normalization" },
		{ "ClampMin", "0.0" },
#if !UE_BUILD_SHIPPING
		{ "Comment", "/** Maximum sum of all active curves in this group. */" },
#endif
		{ "ModuleRelativePath", "Public/AnimNode_VrmCurveNormalizer.h" },
#if !UE_BUILD_SHIPPING
		{ "ToolTip", "Maximum sum of all active curves in this group." },
#endif
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Strength_MetaData[] = {
		{ "Category", "Curve Normalization" },
		{ "ClampMax", "1.0" },
		{ "ClampMin", "0.0" },
#if !UE_BUILD_SHIPPING
		{ "Comment", "/** 0 leaves the source unchanged; 1 applies the full normalization. */" },
#endif
		{ "ModuleRelativePath", "Public/AnimNode_VrmCurveNormalizer.h" },
#if !UE_BUILD_SHIPPING
		{ "ToolTip", "0 leaves the source unchanged; 1 applies the full normalization." },
#endif
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FNamePropertyParams NewProp_CurveNames_Inner;
	static const UECodeGen_Private::FArrayPropertyParams NewProp_CurveNames;
	static const UECodeGen_Private::FFloatPropertyParams NewProp_MaximumCombinedValue;
	static const UECodeGen_Private::FFloatPropertyParams NewProp_Strength;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static void* NewStructOps()
	{
		return (UScriptStruct::ICppStructOps*)new UScriptStruct::TCppStructOps<FVrmCurveNormalizationGroup>();
	}
	static const UECodeGen_Private::FStructParams StructParams;
};
const UECodeGen_Private::FNamePropertyParams Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics::NewProp_CurveNames_Inner = { "CurveNames", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Name, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FArrayPropertyParams Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics::NewProp_CurveNames = { "CurveNames", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Array, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(FVrmCurveNormalizationGroup, CurveNames), EArrayPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_CurveNames_MetaData), NewProp_CurveNames_MetaData) };
const UECodeGen_Private::FFloatPropertyParams Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics::NewProp_MaximumCombinedValue = { "MaximumCombinedValue", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Float, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(FVrmCurveNormalizationGroup, MaximumCombinedValue), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_MaximumCombinedValue_MetaData), NewProp_MaximumCombinedValue_MetaData) };
const UECodeGen_Private::FFloatPropertyParams Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics::NewProp_Strength = { "Strength", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Float, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(FVrmCurveNormalizationGroup, Strength), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Strength_MetaData), NewProp_Strength_MetaData) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics::NewProp_CurveNames_Inner,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics::NewProp_CurveNames,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics::NewProp_MaximumCombinedValue,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics::NewProp_Strength,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics::PropPointers) < 2048);
const UECodeGen_Private::FStructParams Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics::StructParams = {
	(UObject* (*)())Z_Construct_UPackage__Script_VRM4U,
	nullptr,
	&NewStructOps,
	"VrmCurveNormalizationGroup",
	Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics::PropPointers,
	UE_ARRAY_COUNT(Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics::PropPointers),
	sizeof(FVrmCurveNormalizationGroup),
	alignof(FVrmCurveNormalizationGroup),
	RF_Public|RF_Transient|RF_MarkAsNative,
	EStructFlags(0x00000201),
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics::Struct_MetaDataParams), Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics::Struct_MetaDataParams)
};
UScriptStruct* Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup()
{
	if (!Z_Registration_Info_UScriptStruct_FVrmCurveNormalizationGroup.InnerSingleton)
	{
		UECodeGen_Private::ConstructUScriptStruct(Z_Registration_Info_UScriptStruct_FVrmCurveNormalizationGroup.InnerSingleton, Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics::StructParams);
	}
	return Z_Registration_Info_UScriptStruct_FVrmCurveNormalizationGroup.InnerSingleton;
}
// ********** End ScriptStruct FVrmCurveNormalizationGroup *****************************************

// ********** Begin ScriptStruct FAnimNode_VrmCurveNormalizer **************************************
static_assert(std::is_polymorphic<FAnimNode_VrmCurveNormalizer>() == std::is_polymorphic<FAnimNode_Base>(), "USTRUCT FAnimNode_VrmCurveNormalizer cannot be polymorphic unless super FAnimNode_Base is polymorphic");
static FStructRegistrationInfo Z_Registration_Info_UScriptStruct_FAnimNode_VrmCurveNormalizer;
class UScriptStruct* FAnimNode_VrmCurveNormalizer::StaticStruct()
{
	if (!Z_Registration_Info_UScriptStruct_FAnimNode_VrmCurveNormalizer.OuterSingleton)
	{
		Z_Registration_Info_UScriptStruct_FAnimNode_VrmCurveNormalizer.OuterSingleton = GetStaticStruct(Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer, (UObject*)Z_Construct_UPackage__Script_VRM4U(), TEXT("AnimNode_VrmCurveNormalizer"));
	}
	return Z_Registration_Info_UScriptStruct_FAnimNode_VrmCurveNormalizer.OuterSingleton;
}
struct Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Struct_MetaDataParams[] = {
		{ "BlueprintInternalUseOnly", "true" },
		{ "BlueprintType", "true" },
#if !UE_BUILD_SHIPPING
		{ "Comment", "/**\n * Normalizes animation curves after evaluating the input pose.\n *\n * The defaults are conservative PerfectSync/ARKit mouth corrections, but the\n * normalization groups are editable and can be used for arbitrary curves.\n * Place this node after the PoseAsset node, including in a Post Process AnimBP.\n */" },
#endif
		{ "ModuleRelativePath", "Public/AnimNode_VrmCurveNormalizer.h" },
#if !UE_BUILD_SHIPPING
		{ "ToolTip", "Normalizes animation curves after evaluating the input pose.\n\nThe defaults are conservative PerfectSync/ARKit mouth corrections, but the\nnormalization groups are editable and can be used for arbitrary curves.\nPlace this node after the PoseAsset node, including in a Post Process AnimBP." },
#endif
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_SourcePose_MetaData[] = {
		{ "Category", "Links" },
		{ "ModuleRelativePath", "Public/AnimNode_VrmCurveNormalizer.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_bClampPerfectSyncCurves_MetaData[] = {
		{ "Category", "Settings" },
#if !UE_BUILD_SHIPPING
		{ "Comment", "/** Applies the built-in 0-1 clamp to the 52 PerfectSync/ARKit face curves. */" },
#endif
		{ "ModuleRelativePath", "Public/AnimNode_VrmCurveNormalizer.h" },
		{ "PinHiddenByDefault", "" },
#if !UE_BUILD_SHIPPING
		{ "ToolTip", "Applies the built-in 0-1 clamp to the 52 PerfectSync/ARKit face curves." },
#endif
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_NormalizationGroups_MetaData[] = {
		{ "Category", "Settings" },
		{ "ModuleRelativePath", "Public/AnimNode_VrmCurveNormalizer.h" },
		{ "PinHiddenByDefault", "" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Alpha_MetaData[] = {
		{ "Category", "Settings" },
		{ "ClampMax", "1.0" },
		{ "ClampMin", "0.0" },
#if !UE_BUILD_SHIPPING
		{ "Comment", "/** Overall correction amount. */" },
#endif
		{ "ModuleRelativePath", "Public/AnimNode_VrmCurveNormalizer.h" },
		{ "PinShownByDefault", "" },
#if !UE_BUILD_SHIPPING
		{ "ToolTip", "Overall correction amount." },
#endif
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FStructPropertyParams NewProp_SourcePose;
	static void NewProp_bClampPerfectSyncCurves_SetBit(void* Obj);
	static const UECodeGen_Private::FBoolPropertyParams NewProp_bClampPerfectSyncCurves;
	static const UECodeGen_Private::FStructPropertyParams NewProp_NormalizationGroups_Inner;
	static const UECodeGen_Private::FArrayPropertyParams NewProp_NormalizationGroups;
	static const UECodeGen_Private::FFloatPropertyParams NewProp_Alpha;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static void* NewStructOps()
	{
		return (UScriptStruct::ICppStructOps*)new UScriptStruct::TCppStructOps<FAnimNode_VrmCurveNormalizer>();
	}
	static const UECodeGen_Private::FStructParams StructParams;
};
const UECodeGen_Private::FStructPropertyParams Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::NewProp_SourcePose = { "SourcePose", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(FAnimNode_VrmCurveNormalizer, SourcePose), Z_Construct_UScriptStruct_FPoseLink, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_SourcePose_MetaData), NewProp_SourcePose_MetaData) }; // 798335583
void Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::NewProp_bClampPerfectSyncCurves_SetBit(void* Obj)
{
	((FAnimNode_VrmCurveNormalizer*)Obj)->bClampPerfectSyncCurves = 1;
}
const UECodeGen_Private::FBoolPropertyParams Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::NewProp_bClampPerfectSyncCurves = { "bClampPerfectSyncCurves", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Bool | UECodeGen_Private::EPropertyGenFlags::NativeBool, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, sizeof(bool), sizeof(FAnimNode_VrmCurveNormalizer), &Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::NewProp_bClampPerfectSyncCurves_SetBit, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_bClampPerfectSyncCurves_MetaData), NewProp_bClampPerfectSyncCurves_MetaData) };
const UECodeGen_Private::FStructPropertyParams Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::NewProp_NormalizationGroups_Inner = { "NormalizationGroups", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup, METADATA_PARAMS(0, nullptr) }; // 4232431818
const UECodeGen_Private::FArrayPropertyParams Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::NewProp_NormalizationGroups = { "NormalizationGroups", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Array, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(FAnimNode_VrmCurveNormalizer, NormalizationGroups), EArrayPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_NormalizationGroups_MetaData), NewProp_NormalizationGroups_MetaData) }; // 4232431818
const UECodeGen_Private::FFloatPropertyParams Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::NewProp_Alpha = { "Alpha", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Float, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(FAnimNode_VrmCurveNormalizer, Alpha), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Alpha_MetaData), NewProp_Alpha_MetaData) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::NewProp_SourcePose,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::NewProp_bClampPerfectSyncCurves,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::NewProp_NormalizationGroups_Inner,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::NewProp_NormalizationGroups,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::NewProp_Alpha,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::PropPointers) < 2048);
const UECodeGen_Private::FStructParams Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::StructParams = {
	(UObject* (*)())Z_Construct_UPackage__Script_VRM4U,
	Z_Construct_UScriptStruct_FAnimNode_Base,
	&NewStructOps,
	"AnimNode_VrmCurveNormalizer",
	Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::PropPointers,
	UE_ARRAY_COUNT(Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::PropPointers),
	sizeof(FAnimNode_VrmCurveNormalizer),
	alignof(FAnimNode_VrmCurveNormalizer),
	RF_Public|RF_Transient|RF_MarkAsNative,
	EStructFlags(0x00000201),
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::Struct_MetaDataParams), Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::Struct_MetaDataParams)
};
UScriptStruct* Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer()
{
	if (!Z_Registration_Info_UScriptStruct_FAnimNode_VrmCurveNormalizer.InnerSingleton)
	{
		UECodeGen_Private::ConstructUScriptStruct(Z_Registration_Info_UScriptStruct_FAnimNode_VrmCurveNormalizer.InnerSingleton, Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::StructParams);
	}
	return Z_Registration_Info_UScriptStruct_FAnimNode_VrmCurveNormalizer.InnerSingleton;
}
// ********** End ScriptStruct FAnimNode_VrmCurveNormalizer ****************************************

// ********** Begin Registration *******************************************************************
struct Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_VRM4U_Source_VRM4U_Public_AnimNode_VrmCurveNormalizer_h__Script_VRM4U_Statics
{
	static constexpr FStructRegisterCompiledInInfo ScriptStructInfo[] = {
		{ FVrmCurveNormalizationGroup::StaticStruct, Z_Construct_UScriptStruct_FVrmCurveNormalizationGroup_Statics::NewStructOps, TEXT("VrmCurveNormalizationGroup"), &Z_Registration_Info_UScriptStruct_FVrmCurveNormalizationGroup, CONSTRUCT_RELOAD_VERSION_INFO(FStructReloadVersionInfo, sizeof(FVrmCurveNormalizationGroup), 4232431818U) },
		{ FAnimNode_VrmCurveNormalizer::StaticStruct, Z_Construct_UScriptStruct_FAnimNode_VrmCurveNormalizer_Statics::NewStructOps, TEXT("AnimNode_VrmCurveNormalizer"), &Z_Registration_Info_UScriptStruct_FAnimNode_VrmCurveNormalizer, CONSTRUCT_RELOAD_VERSION_INFO(FStructReloadVersionInfo, sizeof(FAnimNode_VrmCurveNormalizer), 3301622009U) },
	};
};
static FRegisterCompiledInInfo Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_VRM4U_Source_VRM4U_Public_AnimNode_VrmCurveNormalizer_h__Script_VRM4U_3518319923(TEXT("/Script/VRM4U"),
	nullptr, 0,
	Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_VRM4U_Source_VRM4U_Public_AnimNode_VrmCurveNormalizer_h__Script_VRM4U_Statics::ScriptStructInfo, UE_ARRAY_COUNT(Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_VRM4U_Source_VRM4U_Public_AnimNode_VrmCurveNormalizer_h__Script_VRM4U_Statics::ScriptStructInfo),
	nullptr, 0);
// ********** End Registration *********************************************************************

PRAGMA_ENABLE_DEPRECATION_WARNINGS
