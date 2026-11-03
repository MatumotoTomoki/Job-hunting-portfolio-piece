// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
#include "EffekseerSystemComponent.h"
#include "EffekseerHandle.h"

PRAGMA_DISABLE_DEPRECATION_WARNINGS

void EmptyLinkFunctionForGeneratedCodeEffekseerSystemComponent() {}

// ********** Begin Cross Module References ********************************************************
COREUOBJECT_API UScriptStruct* Z_Construct_UScriptStruct_FColor();
COREUOBJECT_API UScriptStruct* Z_Construct_UScriptStruct_FQuat();
COREUOBJECT_API UScriptStruct* Z_Construct_UScriptStruct_FVector();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerEffect_NoRegister();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_NoRegister();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerSystemComponent();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerSystemComponent_NoRegister();
EFFEKSEER_API UEnum* Z_Construct_UEnum_Effekseer_EEffekseerColorSpaceType();
EFFEKSEER_API UScriptStruct* Z_Construct_UScriptStruct_FEffekseerHandle();
ENGINE_API UClass* Z_Construct_UClass_UMaterialInstanceConstant_NoRegister();
ENGINE_API UClass* Z_Construct_UClass_UMaterialInstanceDynamic_NoRegister();
ENGINE_API UClass* Z_Construct_UClass_UPrimitiveComponent();
ENGINE_API UClass* Z_Construct_UClass_UTexture2D_NoRegister();
UPackage* Z_Construct_UPackage__Script_Effekseer();
// ********** End Cross Module References **********************************************************

// ********** Begin Class UEffekseerSystemComponent Function Exists ********************************
struct Z_Construct_UFunction_UEffekseerSystemComponent_Exists_Statics
{
	struct EffekseerSystemComponent_eventExists_Parms
	{
		FEffekseerHandle handle;
		bool ReturnValue;
	};
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "Category", "Control" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FStructPropertyParams NewProp_handle;
	static void NewProp_ReturnValue_SetBit(void* Obj);
	static const UECodeGen_Private::FBoolPropertyParams NewProp_ReturnValue;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
const UECodeGen_Private::FStructPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_Exists_Statics::NewProp_handle = { "handle", nullptr, (EPropertyFlags)0x0010008000000080, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventExists_Parms, handle), Z_Construct_UScriptStruct_FEffekseerHandle, METADATA_PARAMS(0, nullptr) }; // 4118386477
void Z_Construct_UFunction_UEffekseerSystemComponent_Exists_Statics::NewProp_ReturnValue_SetBit(void* Obj)
{
	((EffekseerSystemComponent_eventExists_Parms*)Obj)->ReturnValue = 1;
}
const UECodeGen_Private::FBoolPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_Exists_Statics::NewProp_ReturnValue = { "ReturnValue", nullptr, (EPropertyFlags)0x0010000000000580, UECodeGen_Private::EPropertyGenFlags::Bool | UECodeGen_Private::EPropertyGenFlags::NativeBool, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, sizeof(bool), sizeof(EffekseerSystemComponent_eventExists_Parms), &Z_Construct_UFunction_UEffekseerSystemComponent_Exists_Statics::NewProp_ReturnValue_SetBit, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UFunction_UEffekseerSystemComponent_Exists_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_Exists_Statics::NewProp_handle,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_Exists_Statics::NewProp_ReturnValue,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_Exists_Statics::PropPointers) < 2048);
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerSystemComponent_Exists_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerSystemComponent, nullptr, "Exists", Z_Construct_UFunction_UEffekseerSystemComponent_Exists_Statics::PropPointers, UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_Exists_Statics::PropPointers), sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_Exists_Statics::EffekseerSystemComponent_eventExists_Parms), RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x54020401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_Exists_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerSystemComponent_Exists_Statics::Function_MetaDataParams)},  };
static_assert(sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_Exists_Statics::EffekseerSystemComponent_eventExists_Parms) < MAX_uint16);
UFunction* Z_Construct_UFunction_UEffekseerSystemComponent_Exists()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerSystemComponent_Exists_Statics::FuncParams);
	}
	return ReturnFunction;
}
DEFINE_FUNCTION(UEffekseerSystemComponent::execExists)
{
	P_GET_STRUCT(FEffekseerHandle,Z_Param_handle);
	P_FINISH;
	P_NATIVE_BEGIN;
	*(bool*)Z_Param__Result=P_THIS->Exists(Z_Param_handle);
	P_NATIVE_END;
}
// ********** End Class UEffekseerSystemComponent Function Exists **********************************

// ********** Begin Class UEffekseerSystemComponent Function Play **********************************
struct Z_Construct_UFunction_UEffekseerSystemComponent_Play_Statics
{
	struct EffekseerSystemComponent_eventPlay_Parms
	{
		UEffekseerEffect* effect;
		FVector position;
		FEffekseerHandle ReturnValue;
	};
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "Category", "Control" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FObjectPropertyParams NewProp_effect;
	static const UECodeGen_Private::FStructPropertyParams NewProp_position;
	static const UECodeGen_Private::FStructPropertyParams NewProp_ReturnValue;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_Play_Statics::NewProp_effect = { "effect", nullptr, (EPropertyFlags)0x0010000000000080, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventPlay_Parms, effect), Z_Construct_UClass_UEffekseerEffect_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FStructPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_Play_Statics::NewProp_position = { "position", nullptr, (EPropertyFlags)0x0010000000000080, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventPlay_Parms, position), Z_Construct_UScriptStruct_FVector, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FStructPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_Play_Statics::NewProp_ReturnValue = { "ReturnValue", nullptr, (EPropertyFlags)0x0010008000000580, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventPlay_Parms, ReturnValue), Z_Construct_UScriptStruct_FEffekseerHandle, METADATA_PARAMS(0, nullptr) }; // 4118386477
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UFunction_UEffekseerSystemComponent_Play_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_Play_Statics::NewProp_effect,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_Play_Statics::NewProp_position,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_Play_Statics::NewProp_ReturnValue,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_Play_Statics::PropPointers) < 2048);
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerSystemComponent_Play_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerSystemComponent, nullptr, "Play", Z_Construct_UFunction_UEffekseerSystemComponent_Play_Statics::PropPointers, UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_Play_Statics::PropPointers), sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_Play_Statics::EffekseerSystemComponent_eventPlay_Parms), RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x04820401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_Play_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerSystemComponent_Play_Statics::Function_MetaDataParams)},  };
static_assert(sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_Play_Statics::EffekseerSystemComponent_eventPlay_Parms) < MAX_uint16);
UFunction* Z_Construct_UFunction_UEffekseerSystemComponent_Play()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerSystemComponent_Play_Statics::FuncParams);
	}
	return ReturnFunction;
}
DEFINE_FUNCTION(UEffekseerSystemComponent::execPlay)
{
	P_GET_OBJECT(UEffekseerEffect,Z_Param_effect);
	P_GET_STRUCT(FVector,Z_Param_position);
	P_FINISH;
	P_NATIVE_BEGIN;
	*(FEffekseerHandle*)Z_Param__Result=P_THIS->Play(Z_Param_effect,Z_Param_position);
	P_NATIVE_END;
}
// ********** End Class UEffekseerSystemComponent Function Play ************************************

// ********** Begin Class UEffekseerSystemComponent Function SendTrigger ***************************
struct Z_Construct_UFunction_UEffekseerSystemComponent_SendTrigger_Statics
{
	struct EffekseerSystemComponent_eventSendTrigger_Parms
	{
		FEffekseerHandle handle;
		int32 index;
	};
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "Category", "Control" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FStructPropertyParams NewProp_handle;
	static const UECodeGen_Private::FIntPropertyParams NewProp_index;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
const UECodeGen_Private::FStructPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_SendTrigger_Statics::NewProp_handle = { "handle", nullptr, (EPropertyFlags)0x0010008000000080, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventSendTrigger_Parms, handle), Z_Construct_UScriptStruct_FEffekseerHandle, METADATA_PARAMS(0, nullptr) }; // 4118386477
const UECodeGen_Private::FIntPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_SendTrigger_Statics::NewProp_index = { "index", nullptr, (EPropertyFlags)0x0010000000000080, UECodeGen_Private::EPropertyGenFlags::Int, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventSendTrigger_Parms, index), METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UFunction_UEffekseerSystemComponent_SendTrigger_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_SendTrigger_Statics::NewProp_handle,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_SendTrigger_Statics::NewProp_index,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SendTrigger_Statics::PropPointers) < 2048);
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerSystemComponent_SendTrigger_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerSystemComponent, nullptr, "SendTrigger", Z_Construct_UFunction_UEffekseerSystemComponent_SendTrigger_Statics::PropPointers, UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SendTrigger_Statics::PropPointers), sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_SendTrigger_Statics::EffekseerSystemComponent_eventSendTrigger_Parms), RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x04020401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SendTrigger_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerSystemComponent_SendTrigger_Statics::Function_MetaDataParams)},  };
static_assert(sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_SendTrigger_Statics::EffekseerSystemComponent_eventSendTrigger_Parms) < MAX_uint16);
UFunction* Z_Construct_UFunction_UEffekseerSystemComponent_SendTrigger()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerSystemComponent_SendTrigger_Statics::FuncParams);
	}
	return ReturnFunction;
}
DEFINE_FUNCTION(UEffekseerSystemComponent::execSendTrigger)
{
	P_GET_STRUCT(FEffekseerHandle,Z_Param_handle);
	P_GET_PROPERTY(FIntProperty,Z_Param_index);
	P_FINISH;
	P_NATIVE_BEGIN;
	P_THIS->SendTrigger(Z_Param_handle,Z_Param_index);
	P_NATIVE_END;
}
// ********** End Class UEffekseerSystemComponent Function SendTrigger *****************************

// ********** Begin Class UEffekseerSystemComponent Function SetEffectAllColor *********************
struct Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectAllColor_Statics
{
	struct EffekseerSystemComponent_eventSetEffectAllColor_Parms
	{
		FEffekseerHandle handle;
		FColor color;
	};
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "Category", "Control" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FStructPropertyParams NewProp_handle;
	static const UECodeGen_Private::FStructPropertyParams NewProp_color;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
const UECodeGen_Private::FStructPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectAllColor_Statics::NewProp_handle = { "handle", nullptr, (EPropertyFlags)0x0010008000000080, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventSetEffectAllColor_Parms, handle), Z_Construct_UScriptStruct_FEffekseerHandle, METADATA_PARAMS(0, nullptr) }; // 4118386477
const UECodeGen_Private::FStructPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectAllColor_Statics::NewProp_color = { "color", nullptr, (EPropertyFlags)0x0010000000000080, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventSetEffectAllColor_Parms, color), Z_Construct_UScriptStruct_FColor, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectAllColor_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectAllColor_Statics::NewProp_handle,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectAllColor_Statics::NewProp_color,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectAllColor_Statics::PropPointers) < 2048);
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectAllColor_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerSystemComponent, nullptr, "SetEffectAllColor", Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectAllColor_Statics::PropPointers, UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectAllColor_Statics::PropPointers), sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectAllColor_Statics::EffekseerSystemComponent_eventSetEffectAllColor_Parms), RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x04820401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectAllColor_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectAllColor_Statics::Function_MetaDataParams)},  };
static_assert(sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectAllColor_Statics::EffekseerSystemComponent_eventSetEffectAllColor_Parms) < MAX_uint16);
UFunction* Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectAllColor()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectAllColor_Statics::FuncParams);
	}
	return ReturnFunction;
}
DEFINE_FUNCTION(UEffekseerSystemComponent::execSetEffectAllColor)
{
	P_GET_STRUCT(FEffekseerHandle,Z_Param_handle);
	P_GET_STRUCT(FColor,Z_Param_color);
	P_FINISH;
	P_NATIVE_BEGIN;
	P_THIS->SetEffectAllColor(Z_Param_handle,Z_Param_color);
	P_NATIVE_END;
}
// ********** End Class UEffekseerSystemComponent Function SetEffectAllColor ***********************

// ********** Begin Class UEffekseerSystemComponent Function SetEffectDynamicInput *****************
struct Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput_Statics
{
	struct EffekseerSystemComponent_eventSetEffectDynamicInput_Parms
	{
		FEffekseerHandle handle;
		int32 index;
		float value;
	};
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "Category", "Control" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FStructPropertyParams NewProp_handle;
	static const UECodeGen_Private::FIntPropertyParams NewProp_index;
	static const UECodeGen_Private::FFloatPropertyParams NewProp_value;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
const UECodeGen_Private::FStructPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput_Statics::NewProp_handle = { "handle", nullptr, (EPropertyFlags)0x0010008000000080, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventSetEffectDynamicInput_Parms, handle), Z_Construct_UScriptStruct_FEffekseerHandle, METADATA_PARAMS(0, nullptr) }; // 4118386477
const UECodeGen_Private::FIntPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput_Statics::NewProp_index = { "index", nullptr, (EPropertyFlags)0x0010000000000080, UECodeGen_Private::EPropertyGenFlags::Int, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventSetEffectDynamicInput_Parms, index), METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FFloatPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput_Statics::NewProp_value = { "value", nullptr, (EPropertyFlags)0x0010000000000080, UECodeGen_Private::EPropertyGenFlags::Float, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventSetEffectDynamicInput_Parms, value), METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput_Statics::NewProp_handle,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput_Statics::NewProp_index,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput_Statics::NewProp_value,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput_Statics::PropPointers) < 2048);
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerSystemComponent, nullptr, "SetEffectDynamicInput", Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput_Statics::PropPointers, UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput_Statics::PropPointers), sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput_Statics::EffekseerSystemComponent_eventSetEffectDynamicInput_Parms), RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x04020401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput_Statics::Function_MetaDataParams)},  };
static_assert(sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput_Statics::EffekseerSystemComponent_eventSetEffectDynamicInput_Parms) < MAX_uint16);
UFunction* Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput_Statics::FuncParams);
	}
	return ReturnFunction;
}
DEFINE_FUNCTION(UEffekseerSystemComponent::execSetEffectDynamicInput)
{
	P_GET_STRUCT(FEffekseerHandle,Z_Param_handle);
	P_GET_PROPERTY(FIntProperty,Z_Param_index);
	P_GET_PROPERTY(FFloatProperty,Z_Param_value);
	P_FINISH;
	P_NATIVE_BEGIN;
	P_THIS->SetEffectDynamicInput(Z_Param_handle,Z_Param_index,Z_Param_value);
	P_NATIVE_END;
}
// ********** End Class UEffekseerSystemComponent Function SetEffectDynamicInput *******************

// ********** Begin Class UEffekseerSystemComponent Function SetEffectPosition *********************
struct Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectPosition_Statics
{
	struct EffekseerSystemComponent_eventSetEffectPosition_Parms
	{
		FEffekseerHandle handle;
		FVector position;
	};
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "Category", "Control" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FStructPropertyParams NewProp_handle;
	static const UECodeGen_Private::FStructPropertyParams NewProp_position;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
const UECodeGen_Private::FStructPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectPosition_Statics::NewProp_handle = { "handle", nullptr, (EPropertyFlags)0x0010008000000080, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventSetEffectPosition_Parms, handle), Z_Construct_UScriptStruct_FEffekseerHandle, METADATA_PARAMS(0, nullptr) }; // 4118386477
const UECodeGen_Private::FStructPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectPosition_Statics::NewProp_position = { "position", nullptr, (EPropertyFlags)0x0010000000000080, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventSetEffectPosition_Parms, position), Z_Construct_UScriptStruct_FVector, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectPosition_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectPosition_Statics::NewProp_handle,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectPosition_Statics::NewProp_position,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectPosition_Statics::PropPointers) < 2048);
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectPosition_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerSystemComponent, nullptr, "SetEffectPosition", Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectPosition_Statics::PropPointers, UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectPosition_Statics::PropPointers), sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectPosition_Statics::EffekseerSystemComponent_eventSetEffectPosition_Parms), RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x04820401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectPosition_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectPosition_Statics::Function_MetaDataParams)},  };
static_assert(sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectPosition_Statics::EffekseerSystemComponent_eventSetEffectPosition_Parms) < MAX_uint16);
UFunction* Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectPosition()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectPosition_Statics::FuncParams);
	}
	return ReturnFunction;
}
DEFINE_FUNCTION(UEffekseerSystemComponent::execSetEffectPosition)
{
	P_GET_STRUCT(FEffekseerHandle,Z_Param_handle);
	P_GET_STRUCT(FVector,Z_Param_position);
	P_FINISH;
	P_NATIVE_BEGIN;
	P_THIS->SetEffectPosition(Z_Param_handle,Z_Param_position);
	P_NATIVE_END;
}
// ********** End Class UEffekseerSystemComponent Function SetEffectPosition ***********************

// ********** Begin Class UEffekseerSystemComponent Function SetEffectRotation *********************
struct Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectRotation_Statics
{
	struct EffekseerSystemComponent_eventSetEffectRotation_Parms
	{
		FEffekseerHandle handle;
		FQuat rotation;
	};
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "Category", "Control" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FStructPropertyParams NewProp_handle;
	static const UECodeGen_Private::FStructPropertyParams NewProp_rotation;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
const UECodeGen_Private::FStructPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectRotation_Statics::NewProp_handle = { "handle", nullptr, (EPropertyFlags)0x0010008000000080, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventSetEffectRotation_Parms, handle), Z_Construct_UScriptStruct_FEffekseerHandle, METADATA_PARAMS(0, nullptr) }; // 4118386477
const UECodeGen_Private::FStructPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectRotation_Statics::NewProp_rotation = { "rotation", nullptr, (EPropertyFlags)0x0010000000000080, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventSetEffectRotation_Parms, rotation), Z_Construct_UScriptStruct_FQuat, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectRotation_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectRotation_Statics::NewProp_handle,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectRotation_Statics::NewProp_rotation,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectRotation_Statics::PropPointers) < 2048);
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectRotation_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerSystemComponent, nullptr, "SetEffectRotation", Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectRotation_Statics::PropPointers, UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectRotation_Statics::PropPointers), sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectRotation_Statics::EffekseerSystemComponent_eventSetEffectRotation_Parms), RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x04820401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectRotation_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectRotation_Statics::Function_MetaDataParams)},  };
static_assert(sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectRotation_Statics::EffekseerSystemComponent_eventSetEffectRotation_Parms) < MAX_uint16);
UFunction* Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectRotation()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectRotation_Statics::FuncParams);
	}
	return ReturnFunction;
}
DEFINE_FUNCTION(UEffekseerSystemComponent::execSetEffectRotation)
{
	P_GET_STRUCT(FEffekseerHandle,Z_Param_handle);
	P_GET_STRUCT(FQuat,Z_Param_rotation);
	P_FINISH;
	P_NATIVE_BEGIN;
	P_THIS->SetEffectRotation(Z_Param_handle,Z_Param_rotation);
	P_NATIVE_END;
}
// ********** End Class UEffekseerSystemComponent Function SetEffectRotation ***********************

// ********** Begin Class UEffekseerSystemComponent Function SetEffectScaling **********************
struct Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectScaling_Statics
{
	struct EffekseerSystemComponent_eventSetEffectScaling_Parms
	{
		FEffekseerHandle handle;
		FVector scaling;
	};
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "Category", "Control" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FStructPropertyParams NewProp_handle;
	static const UECodeGen_Private::FStructPropertyParams NewProp_scaling;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
const UECodeGen_Private::FStructPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectScaling_Statics::NewProp_handle = { "handle", nullptr, (EPropertyFlags)0x0010008000000080, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventSetEffectScaling_Parms, handle), Z_Construct_UScriptStruct_FEffekseerHandle, METADATA_PARAMS(0, nullptr) }; // 4118386477
const UECodeGen_Private::FStructPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectScaling_Statics::NewProp_scaling = { "scaling", nullptr, (EPropertyFlags)0x0010000000000080, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventSetEffectScaling_Parms, scaling), Z_Construct_UScriptStruct_FVector, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectScaling_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectScaling_Statics::NewProp_handle,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectScaling_Statics::NewProp_scaling,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectScaling_Statics::PropPointers) < 2048);
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectScaling_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerSystemComponent, nullptr, "SetEffectScaling", Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectScaling_Statics::PropPointers, UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectScaling_Statics::PropPointers), sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectScaling_Statics::EffekseerSystemComponent_eventSetEffectScaling_Parms), RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x04820401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectScaling_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectScaling_Statics::Function_MetaDataParams)},  };
static_assert(sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectScaling_Statics::EffekseerSystemComponent_eventSetEffectScaling_Parms) < MAX_uint16);
UFunction* Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectScaling()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectScaling_Statics::FuncParams);
	}
	return ReturnFunction;
}
DEFINE_FUNCTION(UEffekseerSystemComponent::execSetEffectScaling)
{
	P_GET_STRUCT(FEffekseerHandle,Z_Param_handle);
	P_GET_STRUCT(FVector,Z_Param_scaling);
	P_FINISH;
	P_NATIVE_BEGIN;
	P_THIS->SetEffectScaling(Z_Param_handle,Z_Param_scaling);
	P_NATIVE_END;
}
// ********** End Class UEffekseerSystemComponent Function SetEffectScaling ************************

// ********** Begin Class UEffekseerSystemComponent Function SetEffectSpeed ************************
struct Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectSpeed_Statics
{
	struct EffekseerSystemComponent_eventSetEffectSpeed_Parms
	{
		FEffekseerHandle handle;
		float speed;
	};
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "Category", "Control" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FStructPropertyParams NewProp_handle;
	static const UECodeGen_Private::FFloatPropertyParams NewProp_speed;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
const UECodeGen_Private::FStructPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectSpeed_Statics::NewProp_handle = { "handle", nullptr, (EPropertyFlags)0x0010008000000080, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventSetEffectSpeed_Parms, handle), Z_Construct_UScriptStruct_FEffekseerHandle, METADATA_PARAMS(0, nullptr) }; // 4118386477
const UECodeGen_Private::FFloatPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectSpeed_Statics::NewProp_speed = { "speed", nullptr, (EPropertyFlags)0x0010000000000080, UECodeGen_Private::EPropertyGenFlags::Float, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventSetEffectSpeed_Parms, speed), METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectSpeed_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectSpeed_Statics::NewProp_handle,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectSpeed_Statics::NewProp_speed,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectSpeed_Statics::PropPointers) < 2048);
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectSpeed_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerSystemComponent, nullptr, "SetEffectSpeed", Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectSpeed_Statics::PropPointers, UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectSpeed_Statics::PropPointers), sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectSpeed_Statics::EffekseerSystemComponent_eventSetEffectSpeed_Parms), RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x04020401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectSpeed_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectSpeed_Statics::Function_MetaDataParams)},  };
static_assert(sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectSpeed_Statics::EffekseerSystemComponent_eventSetEffectSpeed_Parms) < MAX_uint16);
UFunction* Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectSpeed()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectSpeed_Statics::FuncParams);
	}
	return ReturnFunction;
}
DEFINE_FUNCTION(UEffekseerSystemComponent::execSetEffectSpeed)
{
	P_GET_STRUCT(FEffekseerHandle,Z_Param_handle);
	P_GET_PROPERTY(FFloatProperty,Z_Param_speed);
	P_FINISH;
	P_NATIVE_BEGIN;
	P_THIS->SetEffectSpeed(Z_Param_handle,Z_Param_speed);
	P_NATIVE_END;
}
// ********** End Class UEffekseerSystemComponent Function SetEffectSpeed **************************

// ********** Begin Class UEffekseerSystemComponent Function StartNetwork **************************
struct Z_Construct_UFunction_UEffekseerSystemComponent_StartNetwork_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "Category", "Network" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerSystemComponent_StartNetwork_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerSystemComponent, nullptr, "StartNetwork", nullptr, 0, 0, RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x04020401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_StartNetwork_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerSystemComponent_StartNetwork_Statics::Function_MetaDataParams)},  };
UFunction* Z_Construct_UFunction_UEffekseerSystemComponent_StartNetwork()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerSystemComponent_StartNetwork_Statics::FuncParams);
	}
	return ReturnFunction;
}
DEFINE_FUNCTION(UEffekseerSystemComponent::execStartNetwork)
{
	P_FINISH;
	P_NATIVE_BEGIN;
	P_THIS->StartNetwork();
	P_NATIVE_END;
}
// ********** End Class UEffekseerSystemComponent Function StartNetwork ****************************

// ********** Begin Class UEffekseerSystemComponent Function Stop **********************************
struct Z_Construct_UFunction_UEffekseerSystemComponent_Stop_Statics
{
	struct EffekseerSystemComponent_eventStop_Parms
	{
		FEffekseerHandle handle;
	};
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "Category", "Control" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FStructPropertyParams NewProp_handle;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
const UECodeGen_Private::FStructPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_Stop_Statics::NewProp_handle = { "handle", nullptr, (EPropertyFlags)0x0010008000000080, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventStop_Parms, handle), Z_Construct_UScriptStruct_FEffekseerHandle, METADATA_PARAMS(0, nullptr) }; // 4118386477
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UFunction_UEffekseerSystemComponent_Stop_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_Stop_Statics::NewProp_handle,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_Stop_Statics::PropPointers) < 2048);
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerSystemComponent_Stop_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerSystemComponent, nullptr, "Stop", Z_Construct_UFunction_UEffekseerSystemComponent_Stop_Statics::PropPointers, UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_Stop_Statics::PropPointers), sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_Stop_Statics::EffekseerSystemComponent_eventStop_Parms), RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x04020401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_Stop_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerSystemComponent_Stop_Statics::Function_MetaDataParams)},  };
static_assert(sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_Stop_Statics::EffekseerSystemComponent_eventStop_Parms) < MAX_uint16);
UFunction* Z_Construct_UFunction_UEffekseerSystemComponent_Stop()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerSystemComponent_Stop_Statics::FuncParams);
	}
	return ReturnFunction;
}
DEFINE_FUNCTION(UEffekseerSystemComponent::execStop)
{
	P_GET_STRUCT(FEffekseerHandle,Z_Param_handle);
	P_FINISH;
	P_NATIVE_BEGIN;
	P_THIS->Stop(Z_Param_handle);
	P_NATIVE_END;
}
// ********** End Class UEffekseerSystemComponent Function Stop ************************************

// ********** Begin Class UEffekseerSystemComponent Function StopNetwork ***************************
struct Z_Construct_UFunction_UEffekseerSystemComponent_StopNetwork_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "Category", "Network" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerSystemComponent_StopNetwork_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerSystemComponent, nullptr, "StopNetwork", nullptr, 0, 0, RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x04020401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_StopNetwork_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerSystemComponent_StopNetwork_Statics::Function_MetaDataParams)},  };
UFunction* Z_Construct_UFunction_UEffekseerSystemComponent_StopNetwork()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerSystemComponent_StopNetwork_Statics::FuncParams);
	}
	return ReturnFunction;
}
DEFINE_FUNCTION(UEffekseerSystemComponent::execStopNetwork)
{
	P_FINISH;
	P_NATIVE_BEGIN;
	P_THIS->StopNetwork();
	P_NATIVE_END;
}
// ********** End Class UEffekseerSystemComponent Function StopNetwork *****************************

// ********** Begin Class UEffekseerSystemComponent Function StopRoot ******************************
struct Z_Construct_UFunction_UEffekseerSystemComponent_StopRoot_Statics
{
	struct EffekseerSystemComponent_eventStopRoot_Parms
	{
		FEffekseerHandle handle;
	};
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "Category", "Control" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FStructPropertyParams NewProp_handle;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
const UECodeGen_Private::FStructPropertyParams Z_Construct_UFunction_UEffekseerSystemComponent_StopRoot_Statics::NewProp_handle = { "handle", nullptr, (EPropertyFlags)0x0010008000000080, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerSystemComponent_eventStopRoot_Parms, handle), Z_Construct_UScriptStruct_FEffekseerHandle, METADATA_PARAMS(0, nullptr) }; // 4118386477
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UFunction_UEffekseerSystemComponent_StopRoot_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerSystemComponent_StopRoot_Statics::NewProp_handle,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_StopRoot_Statics::PropPointers) < 2048);
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerSystemComponent_StopRoot_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerSystemComponent, nullptr, "StopRoot", Z_Construct_UFunction_UEffekseerSystemComponent_StopRoot_Statics::PropPointers, UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_StopRoot_Statics::PropPointers), sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_StopRoot_Statics::EffekseerSystemComponent_eventStopRoot_Parms), RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x04020401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerSystemComponent_StopRoot_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerSystemComponent_StopRoot_Statics::Function_MetaDataParams)},  };
static_assert(sizeof(Z_Construct_UFunction_UEffekseerSystemComponent_StopRoot_Statics::EffekseerSystemComponent_eventStopRoot_Parms) < MAX_uint16);
UFunction* Z_Construct_UFunction_UEffekseerSystemComponent_StopRoot()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerSystemComponent_StopRoot_Statics::FuncParams);
	}
	return ReturnFunction;
}
DEFINE_FUNCTION(UEffekseerSystemComponent::execStopRoot)
{
	P_GET_STRUCT(FEffekseerHandle,Z_Param_handle);
	P_FINISH;
	P_NATIVE_BEGIN;
	P_THIS->StopRoot(Z_Param_handle);
	P_NATIVE_END;
}
// ********** End Class UEffekseerSystemComponent Function StopRoot ********************************

// ********** Begin Class UEffekseerSystemComponent ************************************************
void UEffekseerSystemComponent::StaticRegisterNativesUEffekseerSystemComponent()
{
	UClass* Class = UEffekseerSystemComponent::StaticClass();
	static const FNameNativePtrPair Funcs[] = {
		{ "Exists", &UEffekseerSystemComponent::execExists },
		{ "Play", &UEffekseerSystemComponent::execPlay },
		{ "SendTrigger", &UEffekseerSystemComponent::execSendTrigger },
		{ "SetEffectAllColor", &UEffekseerSystemComponent::execSetEffectAllColor },
		{ "SetEffectDynamicInput", &UEffekseerSystemComponent::execSetEffectDynamicInput },
		{ "SetEffectPosition", &UEffekseerSystemComponent::execSetEffectPosition },
		{ "SetEffectRotation", &UEffekseerSystemComponent::execSetEffectRotation },
		{ "SetEffectScaling", &UEffekseerSystemComponent::execSetEffectScaling },
		{ "SetEffectSpeed", &UEffekseerSystemComponent::execSetEffectSpeed },
		{ "StartNetwork", &UEffekseerSystemComponent::execStartNetwork },
		{ "Stop", &UEffekseerSystemComponent::execStop },
		{ "StopNetwork", &UEffekseerSystemComponent::execStopNetwork },
		{ "StopRoot", &UEffekseerSystemComponent::execStopRoot },
	};
	FNativeFunctionRegistrar::RegisterFunctions(Class, Funcs, UE_ARRAY_COUNT(Funcs));
}
FClassRegistrationInfo Z_Registration_Info_UClass_UEffekseerSystemComponent;
UClass* UEffekseerSystemComponent::GetPrivateStaticClass()
{
	using TClass = UEffekseerSystemComponent;
	if (!Z_Registration_Info_UClass_UEffekseerSystemComponent.InnerSingleton)
	{
		GetPrivateStaticClassBody(
			StaticPackage(),
			TEXT("EffekseerSystemComponent"),
			Z_Registration_Info_UClass_UEffekseerSystemComponent.InnerSingleton,
			StaticRegisterNativesUEffekseerSystemComponent,
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
	return Z_Registration_Info_UClass_UEffekseerSystemComponent.InnerSingleton;
}
UClass* Z_Construct_UClass_UEffekseerSystemComponent_NoRegister()
{
	return UEffekseerSystemComponent::GetPrivateStaticClass();
}
struct Z_Construct_UClass_UEffekseerSystemComponent_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Class_MetaDataParams[] = {
		{ "BlueprintSpawnableComponent", "" },
		{ "ClassGroupNames", "Effekseer" },
		{ "HideCategories", "Mobility VirtualTexture Trigger" },
		{ "IncludePath", "EffekseerSystemComponent.h" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_MaxSprite_MetaData[] = {
		{ "Category", "Property" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_ColorSpace_MetaData[] = {
		{ "Category", "Property" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_ThreadCount_MetaData[] = {
		{ "Category", "Property" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_OpaqueMaterial_MetaData[] = {
		{ "Category", "Material" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_TranslucentMaterial_MetaData[] = {
		{ "Category", "Material" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_AdditiveMaterial_MetaData[] = {
		{ "Category", "Material" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_SubtractiveMaterial_MetaData[] = {
		{ "Category", "Material" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_ModulateMaterial_MetaData[] = {
		{ "Category", "Material" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_LightingMaterial_MetaData[] = {
		{ "Category", "Material" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_DistortionTranslucentMaterial_MetaData[] = {
		{ "Category", "Material" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_DistortionAdditiveMaterial_MetaData[] = {
		{ "Category", "Material" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Opaque_DD_Material_MetaData[] = {
		{ "Category", "Material" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Translucent_DD_Material_MetaData[] = {
		{ "Category", "Material" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Additive_DD_Material_MetaData[] = {
		{ "Category", "Material" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Subtractive_DD_Material_MetaData[] = {
		{ "Category", "Material" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Modulate_DD_Material_MetaData[] = {
		{ "Category", "Material" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_DistortionTranslucent_DD_Material_MetaData[] = {
		{ "Category", "Material" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_DistortionAdditive_DD_Material_MetaData[] = {
		{ "Category", "Material" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_GeneratedFixedMaterials_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_OpaqueDynamicMaterials_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_TranslucentDynamicMaterials_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_AdditiveDynamicMaterials_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_SubtractiveDynamicMaterials_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_ModulateDynamicMaterials_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_LightingDynamicMaterials_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_DistortionTranslucentDynamicMaterials_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_DistortionAdditiveDynamicMaterials_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_NetworkPort_MetaData[] = {
		{ "Category", "Network" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_DoStartNetworkAutomatically_MetaData[] = {
		{ "Category", "Network" },
		{ "ModuleRelativePath", "Public/EffekseerSystemComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FIntPropertyParams NewProp_MaxSprite;
	static const UECodeGen_Private::FBytePropertyParams NewProp_ColorSpace_Underlying;
	static const UECodeGen_Private::FEnumPropertyParams NewProp_ColorSpace;
	static const UECodeGen_Private::FIntPropertyParams NewProp_ThreadCount;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_OpaqueMaterial;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_TranslucentMaterial;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_AdditiveMaterial;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_SubtractiveMaterial;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_ModulateMaterial;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_LightingMaterial;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_DistortionTranslucentMaterial;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_DistortionAdditiveMaterial;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_Opaque_DD_Material;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_Translucent_DD_Material;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_Additive_DD_Material;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_Subtractive_DD_Material;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_Modulate_DD_Material;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_DistortionTranslucent_DD_Material;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_DistortionAdditive_DD_Material;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_GeneratedFixedMaterials_ValueProp;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_GeneratedFixedMaterials_Key_KeyProp;
	static const UECodeGen_Private::FMapPropertyParams NewProp_GeneratedFixedMaterials;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_OpaqueDynamicMaterials_ValueProp;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_OpaqueDynamicMaterials_Key_KeyProp;
	static const UECodeGen_Private::FMapPropertyParams NewProp_OpaqueDynamicMaterials;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_TranslucentDynamicMaterials_ValueProp;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_TranslucentDynamicMaterials_Key_KeyProp;
	static const UECodeGen_Private::FMapPropertyParams NewProp_TranslucentDynamicMaterials;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_AdditiveDynamicMaterials_ValueProp;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_AdditiveDynamicMaterials_Key_KeyProp;
	static const UECodeGen_Private::FMapPropertyParams NewProp_AdditiveDynamicMaterials;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_SubtractiveDynamicMaterials_ValueProp;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_SubtractiveDynamicMaterials_Key_KeyProp;
	static const UECodeGen_Private::FMapPropertyParams NewProp_SubtractiveDynamicMaterials;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_ModulateDynamicMaterials_ValueProp;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_ModulateDynamicMaterials_Key_KeyProp;
	static const UECodeGen_Private::FMapPropertyParams NewProp_ModulateDynamicMaterials;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_LightingDynamicMaterials_ValueProp;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_LightingDynamicMaterials_Key_KeyProp;
	static const UECodeGen_Private::FMapPropertyParams NewProp_LightingDynamicMaterials;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_DistortionTranslucentDynamicMaterials_ValueProp;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_DistortionTranslucentDynamicMaterials_Key_KeyProp;
	static const UECodeGen_Private::FMapPropertyParams NewProp_DistortionTranslucentDynamicMaterials;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_DistortionAdditiveDynamicMaterials_ValueProp;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_DistortionAdditiveDynamicMaterials_Key_KeyProp;
	static const UECodeGen_Private::FMapPropertyParams NewProp_DistortionAdditiveDynamicMaterials;
	static const UECodeGen_Private::FIntPropertyParams NewProp_NetworkPort;
	static void NewProp_DoStartNetworkAutomatically_SetBit(void* Obj);
	static const UECodeGen_Private::FBoolPropertyParams NewProp_DoStartNetworkAutomatically;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static UObject* (*const DependentSingletons[])();
	static constexpr FClassFunctionLinkInfo FuncInfo[] = {
		{ &Z_Construct_UFunction_UEffekseerSystemComponent_Exists, "Exists" }, // 767116341
		{ &Z_Construct_UFunction_UEffekseerSystemComponent_Play, "Play" }, // 2927766790
		{ &Z_Construct_UFunction_UEffekseerSystemComponent_SendTrigger, "SendTrigger" }, // 1312839477
		{ &Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectAllColor, "SetEffectAllColor" }, // 2086110952
		{ &Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectDynamicInput, "SetEffectDynamicInput" }, // 2269126515
		{ &Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectPosition, "SetEffectPosition" }, // 2943083532
		{ &Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectRotation, "SetEffectRotation" }, // 826939093
		{ &Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectScaling, "SetEffectScaling" }, // 436678151
		{ &Z_Construct_UFunction_UEffekseerSystemComponent_SetEffectSpeed, "SetEffectSpeed" }, // 570399423
		{ &Z_Construct_UFunction_UEffekseerSystemComponent_StartNetwork, "StartNetwork" }, // 1612166049
		{ &Z_Construct_UFunction_UEffekseerSystemComponent_Stop, "Stop" }, // 1658567697
		{ &Z_Construct_UFunction_UEffekseerSystemComponent_StopNetwork, "StopNetwork" }, // 2005872497
		{ &Z_Construct_UFunction_UEffekseerSystemComponent_StopRoot, "StopRoot" }, // 1527074797
	};
	static_assert(UE_ARRAY_COUNT(FuncInfo) < 2048);
	static constexpr FCppClassTypeInfoStatic StaticCppClassTypeInfo = {
		TCppClassTypeTraits<UEffekseerSystemComponent>::IsAbstract,
	};
	static const UECodeGen_Private::FClassParams ClassParams;
};
const UECodeGen_Private::FIntPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_MaxSprite = { "MaxSprite", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Int, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, MaxSprite), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_MaxSprite_MetaData), NewProp_MaxSprite_MetaData) };
const UECodeGen_Private::FBytePropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_ColorSpace_Underlying = { "UnderlyingType", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Byte, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, nullptr, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FEnumPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_ColorSpace = { "ColorSpace", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Enum, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, ColorSpace), Z_Construct_UEnum_Effekseer_EEffekseerColorSpaceType, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_ColorSpace_MetaData), NewProp_ColorSpace_MetaData) }; // 1530459977
const UECodeGen_Private::FIntPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_ThreadCount = { "ThreadCount", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Int, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, ThreadCount), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_ThreadCount_MetaData), NewProp_ThreadCount_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_OpaqueMaterial = { "OpaqueMaterial", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, OpaqueMaterial), Z_Construct_UClass_UMaterialInstanceConstant_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_OpaqueMaterial_MetaData), NewProp_OpaqueMaterial_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_TranslucentMaterial = { "TranslucentMaterial", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, TranslucentMaterial), Z_Construct_UClass_UMaterialInstanceConstant_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_TranslucentMaterial_MetaData), NewProp_TranslucentMaterial_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_AdditiveMaterial = { "AdditiveMaterial", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, AdditiveMaterial), Z_Construct_UClass_UMaterialInstanceConstant_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_AdditiveMaterial_MetaData), NewProp_AdditiveMaterial_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_SubtractiveMaterial = { "SubtractiveMaterial", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, SubtractiveMaterial), Z_Construct_UClass_UMaterialInstanceConstant_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_SubtractiveMaterial_MetaData), NewProp_SubtractiveMaterial_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_ModulateMaterial = { "ModulateMaterial", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, ModulateMaterial), Z_Construct_UClass_UMaterialInstanceConstant_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_ModulateMaterial_MetaData), NewProp_ModulateMaterial_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_LightingMaterial = { "LightingMaterial", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, LightingMaterial), Z_Construct_UClass_UMaterialInstanceConstant_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_LightingMaterial_MetaData), NewProp_LightingMaterial_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionTranslucentMaterial = { "DistortionTranslucentMaterial", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, DistortionTranslucentMaterial), Z_Construct_UClass_UMaterialInstanceConstant_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_DistortionTranslucentMaterial_MetaData), NewProp_DistortionTranslucentMaterial_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionAdditiveMaterial = { "DistortionAdditiveMaterial", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, DistortionAdditiveMaterial), Z_Construct_UClass_UMaterialInstanceConstant_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_DistortionAdditiveMaterial_MetaData), NewProp_DistortionAdditiveMaterial_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_Opaque_DD_Material = { "Opaque_DD_Material", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, Opaque_DD_Material), Z_Construct_UClass_UMaterialInstanceConstant_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Opaque_DD_Material_MetaData), NewProp_Opaque_DD_Material_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_Translucent_DD_Material = { "Translucent_DD_Material", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, Translucent_DD_Material), Z_Construct_UClass_UMaterialInstanceConstant_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Translucent_DD_Material_MetaData), NewProp_Translucent_DD_Material_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_Additive_DD_Material = { "Additive_DD_Material", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, Additive_DD_Material), Z_Construct_UClass_UMaterialInstanceConstant_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Additive_DD_Material_MetaData), NewProp_Additive_DD_Material_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_Subtractive_DD_Material = { "Subtractive_DD_Material", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, Subtractive_DD_Material), Z_Construct_UClass_UMaterialInstanceConstant_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Subtractive_DD_Material_MetaData), NewProp_Subtractive_DD_Material_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_Modulate_DD_Material = { "Modulate_DD_Material", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, Modulate_DD_Material), Z_Construct_UClass_UMaterialInstanceConstant_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Modulate_DD_Material_MetaData), NewProp_Modulate_DD_Material_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionTranslucent_DD_Material = { "DistortionTranslucent_DD_Material", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, DistortionTranslucent_DD_Material), Z_Construct_UClass_UMaterialInstanceConstant_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_DistortionTranslucent_DD_Material_MetaData), NewProp_DistortionTranslucent_DD_Material_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionAdditive_DD_Material = { "DistortionAdditive_DD_Material", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, DistortionAdditive_DD_Material), Z_Construct_UClass_UMaterialInstanceConstant_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_DistortionAdditive_DD_Material_MetaData), NewProp_DistortionAdditive_DD_Material_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_GeneratedFixedMaterials_ValueProp = { "GeneratedFixedMaterials", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 1, Z_Construct_UClass_UMaterialInstanceDynamic_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_GeneratedFixedMaterials_Key_KeyProp = { "GeneratedFixedMaterials_Key", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UClass_UEffekseerEffectMaterialParameterHolder_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FMapPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_GeneratedFixedMaterials = { "GeneratedFixedMaterials", nullptr, (EPropertyFlags)0x0010000000002000, UECodeGen_Private::EPropertyGenFlags::Map, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, GeneratedFixedMaterials), EMapPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_GeneratedFixedMaterials_MetaData), NewProp_GeneratedFixedMaterials_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_OpaqueDynamicMaterials_ValueProp = { "OpaqueDynamicMaterials", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 1, Z_Construct_UClass_UMaterialInstanceDynamic_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_OpaqueDynamicMaterials_Key_KeyProp = { "OpaqueDynamicMaterials_Key", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UClass_UTexture2D_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FMapPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_OpaqueDynamicMaterials = { "OpaqueDynamicMaterials", nullptr, (EPropertyFlags)0x0010000000002000, UECodeGen_Private::EPropertyGenFlags::Map, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, OpaqueDynamicMaterials), EMapPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_OpaqueDynamicMaterials_MetaData), NewProp_OpaqueDynamicMaterials_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_TranslucentDynamicMaterials_ValueProp = { "TranslucentDynamicMaterials", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 1, Z_Construct_UClass_UMaterialInstanceDynamic_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_TranslucentDynamicMaterials_Key_KeyProp = { "TranslucentDynamicMaterials_Key", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UClass_UTexture2D_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FMapPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_TranslucentDynamicMaterials = { "TranslucentDynamicMaterials", nullptr, (EPropertyFlags)0x0010000000002000, UECodeGen_Private::EPropertyGenFlags::Map, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, TranslucentDynamicMaterials), EMapPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_TranslucentDynamicMaterials_MetaData), NewProp_TranslucentDynamicMaterials_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_AdditiveDynamicMaterials_ValueProp = { "AdditiveDynamicMaterials", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 1, Z_Construct_UClass_UMaterialInstanceDynamic_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_AdditiveDynamicMaterials_Key_KeyProp = { "AdditiveDynamicMaterials_Key", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UClass_UTexture2D_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FMapPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_AdditiveDynamicMaterials = { "AdditiveDynamicMaterials", nullptr, (EPropertyFlags)0x0010000000002000, UECodeGen_Private::EPropertyGenFlags::Map, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, AdditiveDynamicMaterials), EMapPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_AdditiveDynamicMaterials_MetaData), NewProp_AdditiveDynamicMaterials_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_SubtractiveDynamicMaterials_ValueProp = { "SubtractiveDynamicMaterials", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 1, Z_Construct_UClass_UMaterialInstanceDynamic_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_SubtractiveDynamicMaterials_Key_KeyProp = { "SubtractiveDynamicMaterials_Key", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UClass_UTexture2D_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FMapPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_SubtractiveDynamicMaterials = { "SubtractiveDynamicMaterials", nullptr, (EPropertyFlags)0x0010000000002000, UECodeGen_Private::EPropertyGenFlags::Map, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, SubtractiveDynamicMaterials), EMapPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_SubtractiveDynamicMaterials_MetaData), NewProp_SubtractiveDynamicMaterials_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_ModulateDynamicMaterials_ValueProp = { "ModulateDynamicMaterials", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 1, Z_Construct_UClass_UMaterialInstanceDynamic_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_ModulateDynamicMaterials_Key_KeyProp = { "ModulateDynamicMaterials_Key", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UClass_UTexture2D_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FMapPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_ModulateDynamicMaterials = { "ModulateDynamicMaterials", nullptr, (EPropertyFlags)0x0010000000002000, UECodeGen_Private::EPropertyGenFlags::Map, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, ModulateDynamicMaterials), EMapPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_ModulateDynamicMaterials_MetaData), NewProp_ModulateDynamicMaterials_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_LightingDynamicMaterials_ValueProp = { "LightingDynamicMaterials", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 1, Z_Construct_UClass_UMaterialInstanceDynamic_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_LightingDynamicMaterials_Key_KeyProp = { "LightingDynamicMaterials_Key", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UClass_UTexture2D_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FMapPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_LightingDynamicMaterials = { "LightingDynamicMaterials", nullptr, (EPropertyFlags)0x0010000000002000, UECodeGen_Private::EPropertyGenFlags::Map, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, LightingDynamicMaterials), EMapPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_LightingDynamicMaterials_MetaData), NewProp_LightingDynamicMaterials_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionTranslucentDynamicMaterials_ValueProp = { "DistortionTranslucentDynamicMaterials", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 1, Z_Construct_UClass_UMaterialInstanceDynamic_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionTranslucentDynamicMaterials_Key_KeyProp = { "DistortionTranslucentDynamicMaterials_Key", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UClass_UTexture2D_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FMapPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionTranslucentDynamicMaterials = { "DistortionTranslucentDynamicMaterials", nullptr, (EPropertyFlags)0x0010000000002000, UECodeGen_Private::EPropertyGenFlags::Map, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, DistortionTranslucentDynamicMaterials), EMapPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_DistortionTranslucentDynamicMaterials_MetaData), NewProp_DistortionTranslucentDynamicMaterials_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionAdditiveDynamicMaterials_ValueProp = { "DistortionAdditiveDynamicMaterials", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 1, Z_Construct_UClass_UMaterialInstanceDynamic_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionAdditiveDynamicMaterials_Key_KeyProp = { "DistortionAdditiveDynamicMaterials_Key", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UClass_UTexture2D_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FMapPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionAdditiveDynamicMaterials = { "DistortionAdditiveDynamicMaterials", nullptr, (EPropertyFlags)0x0010000000002000, UECodeGen_Private::EPropertyGenFlags::Map, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, DistortionAdditiveDynamicMaterials), EMapPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_DistortionAdditiveDynamicMaterials_MetaData), NewProp_DistortionAdditiveDynamicMaterials_MetaData) };
const UECodeGen_Private::FIntPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_NetworkPort = { "NetworkPort", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Int, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerSystemComponent, NetworkPort), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_NetworkPort_MetaData), NewProp_NetworkPort_MetaData) };
void Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DoStartNetworkAutomatically_SetBit(void* Obj)
{
	((UEffekseerSystemComponent*)Obj)->DoStartNetworkAutomatically = 1;
}
const UECodeGen_Private::FBoolPropertyParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DoStartNetworkAutomatically = { "DoStartNetworkAutomatically", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Bool | UECodeGen_Private::EPropertyGenFlags::NativeBool, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, sizeof(bool), sizeof(UEffekseerSystemComponent), &Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DoStartNetworkAutomatically_SetBit, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_DoStartNetworkAutomatically_MetaData), NewProp_DoStartNetworkAutomatically_MetaData) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UClass_UEffekseerSystemComponent_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_MaxSprite,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_ColorSpace_Underlying,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_ColorSpace,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_ThreadCount,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_OpaqueMaterial,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_TranslucentMaterial,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_AdditiveMaterial,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_SubtractiveMaterial,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_ModulateMaterial,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_LightingMaterial,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionTranslucentMaterial,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionAdditiveMaterial,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_Opaque_DD_Material,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_Translucent_DD_Material,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_Additive_DD_Material,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_Subtractive_DD_Material,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_Modulate_DD_Material,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionTranslucent_DD_Material,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionAdditive_DD_Material,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_GeneratedFixedMaterials_ValueProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_GeneratedFixedMaterials_Key_KeyProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_GeneratedFixedMaterials,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_OpaqueDynamicMaterials_ValueProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_OpaqueDynamicMaterials_Key_KeyProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_OpaqueDynamicMaterials,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_TranslucentDynamicMaterials_ValueProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_TranslucentDynamicMaterials_Key_KeyProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_TranslucentDynamicMaterials,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_AdditiveDynamicMaterials_ValueProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_AdditiveDynamicMaterials_Key_KeyProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_AdditiveDynamicMaterials,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_SubtractiveDynamicMaterials_ValueProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_SubtractiveDynamicMaterials_Key_KeyProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_SubtractiveDynamicMaterials,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_ModulateDynamicMaterials_ValueProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_ModulateDynamicMaterials_Key_KeyProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_ModulateDynamicMaterials,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_LightingDynamicMaterials_ValueProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_LightingDynamicMaterials_Key_KeyProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_LightingDynamicMaterials,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionTranslucentDynamicMaterials_ValueProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionTranslucentDynamicMaterials_Key_KeyProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionTranslucentDynamicMaterials,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionAdditiveDynamicMaterials_ValueProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionAdditiveDynamicMaterials_Key_KeyProp,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DistortionAdditiveDynamicMaterials,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_NetworkPort,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerSystemComponent_Statics::NewProp_DoStartNetworkAutomatically,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerSystemComponent_Statics::PropPointers) < 2048);
UObject* (*const Z_Construct_UClass_UEffekseerSystemComponent_Statics::DependentSingletons[])() = {
	(UObject* (*)())Z_Construct_UClass_UPrimitiveComponent,
	(UObject* (*)())Z_Construct_UPackage__Script_Effekseer,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerSystemComponent_Statics::DependentSingletons) < 16);
const UECodeGen_Private::FClassParams Z_Construct_UClass_UEffekseerSystemComponent_Statics::ClassParams = {
	&UEffekseerSystemComponent::StaticClass,
	"Engine",
	&StaticCppClassTypeInfo,
	DependentSingletons,
	FuncInfo,
	Z_Construct_UClass_UEffekseerSystemComponent_Statics::PropPointers,
	nullptr,
	UE_ARRAY_COUNT(DependentSingletons),
	UE_ARRAY_COUNT(FuncInfo),
	UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerSystemComponent_Statics::PropPointers),
	0,
	0x00B000A4u,
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerSystemComponent_Statics::Class_MetaDataParams), Z_Construct_UClass_UEffekseerSystemComponent_Statics::Class_MetaDataParams)
};
UClass* Z_Construct_UClass_UEffekseerSystemComponent()
{
	if (!Z_Registration_Info_UClass_UEffekseerSystemComponent.OuterSingleton)
	{
		UECodeGen_Private::ConstructUClass(Z_Registration_Info_UClass_UEffekseerSystemComponent.OuterSingleton, Z_Construct_UClass_UEffekseerSystemComponent_Statics::ClassParams);
	}
	return Z_Registration_Info_UClass_UEffekseerSystemComponent.OuterSingleton;
}
DEFINE_VTABLE_PTR_HELPER_CTOR(UEffekseerSystemComponent);
// ********** End Class UEffekseerSystemComponent **************************************************

// ********** Begin Registration *******************************************************************
struct Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerSystemComponent_h__Script_Effekseer_Statics
{
	static constexpr FClassRegisterCompiledInInfo ClassInfo[] = {
		{ Z_Construct_UClass_UEffekseerSystemComponent, UEffekseerSystemComponent::StaticClass, TEXT("UEffekseerSystemComponent"), &Z_Registration_Info_UClass_UEffekseerSystemComponent, CONSTRUCT_RELOAD_VERSION_INFO(FClassReloadVersionInfo, sizeof(UEffekseerSystemComponent), 2978276866U) },
	};
};
static FRegisterCompiledInInfo Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerSystemComponent_h__Script_Effekseer_1285649335(TEXT("/Script/Effekseer"),
	Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerSystemComponent_h__Script_Effekseer_Statics::ClassInfo, UE_ARRAY_COUNT(Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerSystemComponent_h__Script_Effekseer_Statics::ClassInfo),
	nullptr, 0,
	nullptr, 0);
// ********** End Registration *********************************************************************

PRAGMA_ENABLE_DEPRECATION_WARNINGS
