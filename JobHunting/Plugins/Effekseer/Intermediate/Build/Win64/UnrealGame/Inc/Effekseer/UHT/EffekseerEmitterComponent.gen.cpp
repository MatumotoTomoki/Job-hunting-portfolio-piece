// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
#include "EffekseerEmitterComponent.h"
#include "Serialization/ArchiveUObjectFromStructuredArchive.h"

PRAGMA_DISABLE_DEPRECATION_WARNINGS

void EmptyLinkFunctionForGeneratedCodeEffekseerEmitterComponent() {}

// ********** Begin Cross Module References ********************************************************
COREUOBJECT_API UScriptStruct* Z_Construct_UScriptStruct_FColor();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerEffect_NoRegister();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerEmitterComponent();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerEmitterComponent_NoRegister();
EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerSystemComponent_NoRegister();
ENGINE_API UClass* Z_Construct_UClass_AActor_NoRegister();
ENGINE_API UClass* Z_Construct_UClass_UMaterialInterface_NoRegister();
ENGINE_API UClass* Z_Construct_UClass_UPrimitiveComponent();
UPackage* Z_Construct_UPackage__Script_Effekseer();
// ********** End Cross Module References **********************************************************

// ********** Begin Class UEffekseerEmitterComponent Function Exists *******************************
struct Z_Construct_UFunction_UEffekseerEmitterComponent_Exists_Statics
{
	struct EffekseerEmitterComponent_eventExists_Parms
	{
		bool ReturnValue;
	};
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "Category", "Effect" },
		{ "ModuleRelativePath", "Public/EffekseerEmitterComponent.h" },
	};
#endif // WITH_METADATA
	static void NewProp_ReturnValue_SetBit(void* Obj);
	static const UECodeGen_Private::FBoolPropertyParams NewProp_ReturnValue;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
void Z_Construct_UFunction_UEffekseerEmitterComponent_Exists_Statics::NewProp_ReturnValue_SetBit(void* Obj)
{
	((EffekseerEmitterComponent_eventExists_Parms*)Obj)->ReturnValue = 1;
}
const UECodeGen_Private::FBoolPropertyParams Z_Construct_UFunction_UEffekseerEmitterComponent_Exists_Statics::NewProp_ReturnValue = { "ReturnValue", nullptr, (EPropertyFlags)0x0010000000000580, UECodeGen_Private::EPropertyGenFlags::Bool | UECodeGen_Private::EPropertyGenFlags::NativeBool, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, sizeof(bool), sizeof(EffekseerEmitterComponent_eventExists_Parms), &Z_Construct_UFunction_UEffekseerEmitterComponent_Exists_Statics::NewProp_ReturnValue_SetBit, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UFunction_UEffekseerEmitterComponent_Exists_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerEmitterComponent_Exists_Statics::NewProp_ReturnValue,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerEmitterComponent_Exists_Statics::PropPointers) < 2048);
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerEmitterComponent_Exists_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerEmitterComponent, nullptr, "Exists", Z_Construct_UFunction_UEffekseerEmitterComponent_Exists_Statics::PropPointers, UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerEmitterComponent_Exists_Statics::PropPointers), sizeof(Z_Construct_UFunction_UEffekseerEmitterComponent_Exists_Statics::EffekseerEmitterComponent_eventExists_Parms), RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x54020401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerEmitterComponent_Exists_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerEmitterComponent_Exists_Statics::Function_MetaDataParams)},  };
static_assert(sizeof(Z_Construct_UFunction_UEffekseerEmitterComponent_Exists_Statics::EffekseerEmitterComponent_eventExists_Parms) < MAX_uint16);
UFunction* Z_Construct_UFunction_UEffekseerEmitterComponent_Exists()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerEmitterComponent_Exists_Statics::FuncParams);
	}
	return ReturnFunction;
}
DEFINE_FUNCTION(UEffekseerEmitterComponent::execExists)
{
	P_FINISH;
	P_NATIVE_BEGIN;
	*(bool*)Z_Param__Result=P_THIS->Exists();
	P_NATIVE_END;
}
// ********** End Class UEffekseerEmitterComponent Function Exists *********************************

// ********** Begin Class UEffekseerEmitterComponent Function Preview ******************************
#if WITH_EDITOR
struct Z_Construct_UFunction_UEffekseerEmitterComponent_Preview_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "CallInEditor", "true" },
		{ "Category", "Effect" },
		{ "ModuleRelativePath", "Public/EffekseerEmitterComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerEmitterComponent_Preview_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerEmitterComponent, nullptr, "Preview", nullptr, 0, 0, RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x24020401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerEmitterComponent_Preview_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerEmitterComponent_Preview_Statics::Function_MetaDataParams)},  };
UFunction* Z_Construct_UFunction_UEffekseerEmitterComponent_Preview()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerEmitterComponent_Preview_Statics::FuncParams);
	}
	return ReturnFunction;
}
#endif // WITH_EDITOR
#if WITH_EDITOR
DEFINE_FUNCTION(UEffekseerEmitterComponent::execPreview)
{
	P_FINISH;
	P_NATIVE_BEGIN;
	P_THIS->Preview();
	P_NATIVE_END;
}
#endif // WITH_EDITOR
// ********** End Class UEffekseerEmitterComponent Function Preview ********************************

// ********** Begin Class UEffekseerEmitterComponent Function SendTrigger **************************
struct Z_Construct_UFunction_UEffekseerEmitterComponent_SendTrigger_Statics
{
	struct EffekseerEmitterComponent_eventSendTrigger_Parms
	{
		int32 index;
	};
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "Category", "Effect" },
		{ "ModuleRelativePath", "Public/EffekseerEmitterComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FIntPropertyParams NewProp_index;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
const UECodeGen_Private::FIntPropertyParams Z_Construct_UFunction_UEffekseerEmitterComponent_SendTrigger_Statics::NewProp_index = { "index", nullptr, (EPropertyFlags)0x0010000000000080, UECodeGen_Private::EPropertyGenFlags::Int, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(EffekseerEmitterComponent_eventSendTrigger_Parms, index), METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UFunction_UEffekseerEmitterComponent_SendTrigger_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_UEffekseerEmitterComponent_SendTrigger_Statics::NewProp_index,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerEmitterComponent_SendTrigger_Statics::PropPointers) < 2048);
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerEmitterComponent_SendTrigger_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerEmitterComponent, nullptr, "SendTrigger", Z_Construct_UFunction_UEffekseerEmitterComponent_SendTrigger_Statics::PropPointers, UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerEmitterComponent_SendTrigger_Statics::PropPointers), sizeof(Z_Construct_UFunction_UEffekseerEmitterComponent_SendTrigger_Statics::EffekseerEmitterComponent_eventSendTrigger_Parms), RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x04020401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerEmitterComponent_SendTrigger_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerEmitterComponent_SendTrigger_Statics::Function_MetaDataParams)},  };
static_assert(sizeof(Z_Construct_UFunction_UEffekseerEmitterComponent_SendTrigger_Statics::EffekseerEmitterComponent_eventSendTrigger_Parms) < MAX_uint16);
UFunction* Z_Construct_UFunction_UEffekseerEmitterComponent_SendTrigger()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerEmitterComponent_SendTrigger_Statics::FuncParams);
	}
	return ReturnFunction;
}
DEFINE_FUNCTION(UEffekseerEmitterComponent::execSendTrigger)
{
	P_GET_PROPERTY(FIntProperty,Z_Param_index);
	P_FINISH;
	P_NATIVE_BEGIN;
	P_THIS->SendTrigger(Z_Param_index);
	P_NATIVE_END;
}
// ********** End Class UEffekseerEmitterComponent Function SendTrigger ****************************

// ********** Begin Class UEffekseerEmitterComponent Function Stop *********************************
struct Z_Construct_UFunction_UEffekseerEmitterComponent_Stop_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "Category", "Effect" },
		{ "ModuleRelativePath", "Public/EffekseerEmitterComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerEmitterComponent_Stop_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerEmitterComponent, nullptr, "Stop", nullptr, 0, 0, RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x04020401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerEmitterComponent_Stop_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerEmitterComponent_Stop_Statics::Function_MetaDataParams)},  };
UFunction* Z_Construct_UFunction_UEffekseerEmitterComponent_Stop()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerEmitterComponent_Stop_Statics::FuncParams);
	}
	return ReturnFunction;
}
DEFINE_FUNCTION(UEffekseerEmitterComponent::execStop)
{
	P_FINISH;
	P_NATIVE_BEGIN;
	P_THIS->Stop();
	P_NATIVE_END;
}
// ********** End Class UEffekseerEmitterComponent Function Stop ***********************************

// ********** Begin Class UEffekseerEmitterComponent Function StopRoot *****************************
struct Z_Construct_UFunction_UEffekseerEmitterComponent_StopRoot_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Function_MetaDataParams[] = {
		{ "Category", "Effect" },
		{ "ModuleRelativePath", "Public/EffekseerEmitterComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FFunctionParams FuncParams;
};
const UECodeGen_Private::FFunctionParams Z_Construct_UFunction_UEffekseerEmitterComponent_StopRoot_Statics::FuncParams = { { (UObject*(*)())Z_Construct_UClass_UEffekseerEmitterComponent, nullptr, "StopRoot", nullptr, 0, 0, RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x04020401, 0, 0, METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UFunction_UEffekseerEmitterComponent_StopRoot_Statics::Function_MetaDataParams), Z_Construct_UFunction_UEffekseerEmitterComponent_StopRoot_Statics::Function_MetaDataParams)},  };
UFunction* Z_Construct_UFunction_UEffekseerEmitterComponent_StopRoot()
{
	static UFunction* ReturnFunction = nullptr;
	if (!ReturnFunction)
	{
		UECodeGen_Private::ConstructUFunction(&ReturnFunction, Z_Construct_UFunction_UEffekseerEmitterComponent_StopRoot_Statics::FuncParams);
	}
	return ReturnFunction;
}
DEFINE_FUNCTION(UEffekseerEmitterComponent::execStopRoot)
{
	P_FINISH;
	P_NATIVE_BEGIN;
	P_THIS->StopRoot();
	P_NATIVE_END;
}
// ********** End Class UEffekseerEmitterComponent Function StopRoot *******************************

// ********** Begin Class UEffekseerEmitterComponent ***********************************************
void UEffekseerEmitterComponent::StaticRegisterNativesUEffekseerEmitterComponent()
{
	UClass* Class = UEffekseerEmitterComponent::StaticClass();
	static const FNameNativePtrPair Funcs[] = {
		{ "Exists", &UEffekseerEmitterComponent::execExists },
#if WITH_EDITOR
		{ "Preview", &UEffekseerEmitterComponent::execPreview },
#endif // WITH_EDITOR
		{ "SendTrigger", &UEffekseerEmitterComponent::execSendTrigger },
		{ "Stop", &UEffekseerEmitterComponent::execStop },
		{ "StopRoot", &UEffekseerEmitterComponent::execStopRoot },
	};
	FNativeFunctionRegistrar::RegisterFunctions(Class, Funcs, UE_ARRAY_COUNT(Funcs));
}
FClassRegistrationInfo Z_Registration_Info_UClass_UEffekseerEmitterComponent;
UClass* UEffekseerEmitterComponent::GetPrivateStaticClass()
{
	using TClass = UEffekseerEmitterComponent;
	if (!Z_Registration_Info_UClass_UEffekseerEmitterComponent.InnerSingleton)
	{
		GetPrivateStaticClassBody(
			StaticPackage(),
			TEXT("EffekseerEmitterComponent"),
			Z_Registration_Info_UClass_UEffekseerEmitterComponent.InnerSingleton,
			StaticRegisterNativesUEffekseerEmitterComponent,
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
	return Z_Registration_Info_UClass_UEffekseerEmitterComponent.InnerSingleton;
}
UClass* Z_Construct_UClass_UEffekseerEmitterComponent_NoRegister()
{
	return UEffekseerEmitterComponent::GetPrivateStaticClass();
}
struct Z_Construct_UClass_UEffekseerEmitterComponent_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Class_MetaDataParams[] = {
		{ "BlueprintSpawnableComponent", "" },
		{ "ClassGroupNames", "Effekseer" },
		{ "HideCategories", "Mobility VirtualTexture Trigger" },
		{ "IncludePath", "EffekseerEmitterComponent.h" },
		{ "ModuleRelativePath", "Public/EffekseerEmitterComponent.h" },
		{ "ObjectInitializerConstructorDeclared", "" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_lastPlayingEffect_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEmitterComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_materials__MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEmitterComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_bAutoDestroy_MetaData[] = {
		{ "ModuleRelativePath", "Public/EffekseerEmitterComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Effect_MetaData[] = {
		{ "Category", "Effect" },
		{ "ModuleRelativePath", "Public/EffekseerEmitterComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_System_MetaData[] = {
		{ "Category", "Effect" },
		{ "ModuleRelativePath", "Public/EffekseerEmitterComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_IsLooping_MetaData[] = {
		{ "Category", "Property" },
		{ "ModuleRelativePath", "Public/EffekseerEmitterComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_AllColor_MetaData[] = {
		{ "Category", "Property" },
		{ "ModuleRelativePath", "Public/EffekseerEmitterComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_Speed_MetaData[] = {
		{ "Category", "Property" },
		{ "ModuleRelativePath", "Public/EffekseerEmitterComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_DynamicInput_MetaData[] = {
		{ "Category", "Property" },
		{ "ModuleRelativePath", "Public/EffekseerEmitterComponent.h" },
	};
	static constexpr UECodeGen_Private::FMetaDataPairParam NewProp_system__MetaData[] = {
		{ "EditInline", "true" },
		{ "ModuleRelativePath", "Public/EffekseerEmitterComponent.h" },
	};
#endif // WITH_METADATA
	static const UECodeGen_Private::FObjectPropertyParams NewProp_lastPlayingEffect;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_materials__Inner;
	static const UECodeGen_Private::FArrayPropertyParams NewProp_materials_;
	static void NewProp_bAutoDestroy_SetBit(void* Obj);
	static const UECodeGen_Private::FBoolPropertyParams NewProp_bAutoDestroy;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_Effect;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_System;
	static void NewProp_IsLooping_SetBit(void* Obj);
	static const UECodeGen_Private::FBoolPropertyParams NewProp_IsLooping;
	static const UECodeGen_Private::FStructPropertyParams NewProp_AllColor;
	static const UECodeGen_Private::FFloatPropertyParams NewProp_Speed;
	static const UECodeGen_Private::FFloatPropertyParams NewProp_DynamicInput_Inner;
	static const UECodeGen_Private::FArrayPropertyParams NewProp_DynamicInput;
	static const UECodeGen_Private::FObjectPropertyParams NewProp_system_;
	static const UECodeGen_Private::FPropertyParamsBase* const PropPointers[];
	static UObject* (*const DependentSingletons[])();
	static constexpr FClassFunctionLinkInfo FuncInfo[] = {
		{ &Z_Construct_UFunction_UEffekseerEmitterComponent_Exists, "Exists" }, // 3825220620
#if WITH_EDITOR
		{ &Z_Construct_UFunction_UEffekseerEmitterComponent_Preview, "Preview" }, // 3808362785
#endif // WITH_EDITOR
		{ &Z_Construct_UFunction_UEffekseerEmitterComponent_SendTrigger, "SendTrigger" }, // 3659647780
		{ &Z_Construct_UFunction_UEffekseerEmitterComponent_Stop, "Stop" }, // 3207345781
		{ &Z_Construct_UFunction_UEffekseerEmitterComponent_StopRoot, "StopRoot" }, // 2312766635
	};
	static_assert(UE_ARRAY_COUNT(FuncInfo) < 2048);
	static constexpr FCppClassTypeInfoStatic StaticCppClassTypeInfo = {
		TCppClassTypeTraits<UEffekseerEmitterComponent>::IsAbstract,
	};
	static const UECodeGen_Private::FClassParams ClassParams;
};
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_lastPlayingEffect = { "lastPlayingEffect", nullptr, (EPropertyFlags)0x0040000000002000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEmitterComponent, lastPlayingEffect), Z_Construct_UClass_UEffekseerEffect_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_lastPlayingEffect_MetaData), NewProp_lastPlayingEffect_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_materials__Inner = { "materials_", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, Z_Construct_UClass_UMaterialInterface_NoRegister, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FArrayPropertyParams Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_materials_ = { "materials_", nullptr, (EPropertyFlags)0x0040000000002000, UECodeGen_Private::EPropertyGenFlags::Array, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEmitterComponent, materials_), EArrayPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_materials__MetaData), NewProp_materials__MetaData) };
void Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_bAutoDestroy_SetBit(void* Obj)
{
	((UEffekseerEmitterComponent*)Obj)->bAutoDestroy = 1;
}
const UECodeGen_Private::FBoolPropertyParams Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_bAutoDestroy = { "bAutoDestroy", nullptr, (EPropertyFlags)0x0010000000000000, UECodeGen_Private::EPropertyGenFlags::Bool , RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, sizeof(uint8), sizeof(UEffekseerEmitterComponent), &Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_bAutoDestroy_SetBit, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_bAutoDestroy_MetaData), NewProp_bAutoDestroy_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_Effect = { "Effect", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEmitterComponent, Effect), Z_Construct_UClass_UEffekseerEffect_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Effect_MetaData), NewProp_Effect_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_System = { "System", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEmitterComponent, System), Z_Construct_UClass_AActor_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_System_MetaData), NewProp_System_MetaData) };
void Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_IsLooping_SetBit(void* Obj)
{
	((UEffekseerEmitterComponent*)Obj)->IsLooping = 1;
}
const UECodeGen_Private::FBoolPropertyParams Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_IsLooping = { "IsLooping", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Bool | UECodeGen_Private::EPropertyGenFlags::NativeBool, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, sizeof(bool), sizeof(UEffekseerEmitterComponent), &Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_IsLooping_SetBit, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_IsLooping_MetaData), NewProp_IsLooping_MetaData) };
const UECodeGen_Private::FStructPropertyParams Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_AllColor = { "AllColor", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Struct, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEmitterComponent, AllColor), Z_Construct_UScriptStruct_FColor, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_AllColor_MetaData), NewProp_AllColor_MetaData) };
const UECodeGen_Private::FFloatPropertyParams Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_Speed = { "Speed", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Float, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEmitterComponent, Speed), METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_Speed_MetaData), NewProp_Speed_MetaData) };
const UECodeGen_Private::FFloatPropertyParams Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_DynamicInput_Inner = { "DynamicInput", nullptr, (EPropertyFlags)0x0000000000000000, UECodeGen_Private::EPropertyGenFlags::Float, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, 0, METADATA_PARAMS(0, nullptr) };
const UECodeGen_Private::FArrayPropertyParams Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_DynamicInput = { "DynamicInput", nullptr, (EPropertyFlags)0x0010000000000005, UECodeGen_Private::EPropertyGenFlags::Array, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEmitterComponent, DynamicInput), EArrayPropertyFlags::None, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_DynamicInput_MetaData), NewProp_DynamicInput_MetaData) };
const UECodeGen_Private::FObjectPropertyParams Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_system_ = { "system_", nullptr, (EPropertyFlags)0x0010000000082008, UECodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, nullptr, nullptr, 1, STRUCT_OFFSET(UEffekseerEmitterComponent, system_), Z_Construct_UClass_UEffekseerSystemComponent_NoRegister, METADATA_PARAMS(UE_ARRAY_COUNT(NewProp_system__MetaData), NewProp_system__MetaData) };
const UECodeGen_Private::FPropertyParamsBase* const Z_Construct_UClass_UEffekseerEmitterComponent_Statics::PropPointers[] = {
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_lastPlayingEffect,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_materials__Inner,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_materials_,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_bAutoDestroy,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_Effect,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_System,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_IsLooping,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_AllColor,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_Speed,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_DynamicInput_Inner,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_DynamicInput,
	(const UECodeGen_Private::FPropertyParamsBase*)&Z_Construct_UClass_UEffekseerEmitterComponent_Statics::NewProp_system_,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerEmitterComponent_Statics::PropPointers) < 2048);
UObject* (*const Z_Construct_UClass_UEffekseerEmitterComponent_Statics::DependentSingletons[])() = {
	(UObject* (*)())Z_Construct_UClass_UPrimitiveComponent,
	(UObject* (*)())Z_Construct_UPackage__Script_Effekseer,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerEmitterComponent_Statics::DependentSingletons) < 16);
const UECodeGen_Private::FClassParams Z_Construct_UClass_UEffekseerEmitterComponent_Statics::ClassParams = {
	&UEffekseerEmitterComponent::StaticClass,
	"Engine",
	&StaticCppClassTypeInfo,
	DependentSingletons,
	FuncInfo,
	Z_Construct_UClass_UEffekseerEmitterComponent_Statics::PropPointers,
	nullptr,
	UE_ARRAY_COUNT(DependentSingletons),
	UE_ARRAY_COUNT(FuncInfo),
	UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerEmitterComponent_Statics::PropPointers),
	0,
	0x00B000A4u,
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UClass_UEffekseerEmitterComponent_Statics::Class_MetaDataParams), Z_Construct_UClass_UEffekseerEmitterComponent_Statics::Class_MetaDataParams)
};
UClass* Z_Construct_UClass_UEffekseerEmitterComponent()
{
	if (!Z_Registration_Info_UClass_UEffekseerEmitterComponent.OuterSingleton)
	{
		UECodeGen_Private::ConstructUClass(Z_Registration_Info_UClass_UEffekseerEmitterComponent.OuterSingleton, Z_Construct_UClass_UEffekseerEmitterComponent_Statics::ClassParams);
	}
	return Z_Registration_Info_UClass_UEffekseerEmitterComponent.OuterSingleton;
}
DEFINE_VTABLE_PTR_HELPER_CTOR(UEffekseerEmitterComponent);
IMPLEMENT_FSTRUCTUREDARCHIVE_SERIALIZER(UEffekseerEmitterComponent)
// ********** End Class UEffekseerEmitterComponent *************************************************

// ********** Begin Registration *******************************************************************
struct Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerEmitterComponent_h__Script_Effekseer_Statics
{
	static constexpr FClassRegisterCompiledInInfo ClassInfo[] = {
		{ Z_Construct_UClass_UEffekseerEmitterComponent, UEffekseerEmitterComponent::StaticClass, TEXT("UEffekseerEmitterComponent"), &Z_Registration_Info_UClass_UEffekseerEmitterComponent, CONSTRUCT_RELOAD_VERSION_INFO(FClassReloadVersionInfo, sizeof(UEffekseerEmitterComponent), 122521786U) },
	};
};
static FRegisterCompiledInInfo Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerEmitterComponent_h__Script_Effekseer_2368216170(TEXT("/Script/Effekseer"),
	Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerEmitterComponent_h__Script_Effekseer_Statics::ClassInfo, UE_ARRAY_COUNT(Z_CompiledInDeferFile_FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerEmitterComponent_h__Script_Effekseer_Statics::ClassInfo),
	nullptr, 0,
	nullptr, 0);
// ********** End Registration *********************************************************************

PRAGMA_ENABLE_DEPRECATION_WARNINGS
