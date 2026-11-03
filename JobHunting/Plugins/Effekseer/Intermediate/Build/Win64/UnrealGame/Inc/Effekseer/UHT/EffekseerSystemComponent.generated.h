// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

// IWYU pragma: private, include "EffekseerSystemComponent.h"

#ifdef EFFEKSEER_EffekseerSystemComponent_generated_h
#error "EffekseerSystemComponent.generated.h already included, missing '#pragma once' in EffekseerSystemComponent.h"
#endif
#define EFFEKSEER_EffekseerSystemComponent_generated_h

#include "UObject/ObjectMacros.h"
#include "UObject/ScriptMacros.h"

PRAGMA_DISABLE_DEPRECATION_WARNINGS

class UEffekseerEffect;
struct FColor;
struct FEffekseerHandle;

// ********** Begin Class UEffekseerSystemComponent ************************************************
#define FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerSystemComponent_h_21_RPC_WRAPPERS_NO_PURE_DECLS \
	DECLARE_FUNCTION(execStopNetwork); \
	DECLARE_FUNCTION(execStartNetwork); \
	DECLARE_FUNCTION(execSetEffectDynamicInput); \
	DECLARE_FUNCTION(execSetEffectAllColor); \
	DECLARE_FUNCTION(execSetEffectSpeed); \
	DECLARE_FUNCTION(execStopRoot); \
	DECLARE_FUNCTION(execStop); \
	DECLARE_FUNCTION(execSendTrigger); \
	DECLARE_FUNCTION(execExists); \
	DECLARE_FUNCTION(execSetEffectScaling); \
	DECLARE_FUNCTION(execSetEffectRotation); \
	DECLARE_FUNCTION(execSetEffectPosition); \
	DECLARE_FUNCTION(execPlay);


EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerSystemComponent_NoRegister();

#define FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerSystemComponent_h_21_INCLASS_NO_PURE_DECLS \
private: \
	static void StaticRegisterNativesUEffekseerSystemComponent(); \
	friend struct Z_Construct_UClass_UEffekseerSystemComponent_Statics; \
	static UClass* GetPrivateStaticClass(); \
	friend EFFEKSEER_API UClass* Z_Construct_UClass_UEffekseerSystemComponent_NoRegister(); \
public: \
	DECLARE_CLASS2(UEffekseerSystemComponent, UPrimitiveComponent, COMPILED_IN_FLAGS(0 | CLASS_Config), CASTCLASS_None, TEXT("/Script/Effekseer"), Z_Construct_UClass_UEffekseerSystemComponent_NoRegister) \
	DECLARE_SERIALIZER(UEffekseerSystemComponent)


#define FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerSystemComponent_h_21_ENHANCED_CONSTRUCTORS \
	/** Deleted move- and copy-constructors, should never be used */ \
	UEffekseerSystemComponent(UEffekseerSystemComponent&&) = delete; \
	UEffekseerSystemComponent(const UEffekseerSystemComponent&) = delete; \
	DECLARE_VTABLE_PTR_HELPER_CTOR(NO_API, UEffekseerSystemComponent); \
	DEFINE_VTABLE_PTR_HELPER_CTOR_CALLER(UEffekseerSystemComponent); \
	DEFINE_DEFAULT_CONSTRUCTOR_CALL(UEffekseerSystemComponent)


#define FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerSystemComponent_h_18_PROLOG
#define FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerSystemComponent_h_21_GENERATED_BODY \
PRAGMA_DISABLE_DEPRECATION_WARNINGS \
public: \
	FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerSystemComponent_h_21_RPC_WRAPPERS_NO_PURE_DECLS \
	FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerSystemComponent_h_21_INCLASS_NO_PURE_DECLS \
	FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerSystemComponent_h_21_ENHANCED_CONSTRUCTORS \
private: \
PRAGMA_ENABLE_DEPRECATION_WARNINGS


class UEffekseerSystemComponent;

// ********** End Class UEffekseerSystemComponent **************************************************

#undef CURRENT_FILE_ID
#define CURRENT_FILE_ID FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerSystemComponent_h

PRAGMA_ENABLE_DEPRECATION_WARNINGS
