// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

// IWYU pragma: private, include "EffekseerAlphaBlendType.h"

#ifdef EFFEKSEER_EffekseerAlphaBlendType_generated_h
#error "EffekseerAlphaBlendType.generated.h already included, missing '#pragma once' in EffekseerAlphaBlendType.h"
#endif
#define EFFEKSEER_EffekseerAlphaBlendType_generated_h

#include "Templates/IsUEnumClass.h"
#include "UObject/ObjectMacros.h"
#include "UObject/ReflectedTypeAccessors.h"

PRAGMA_DISABLE_DEPRECATION_WARNINGS

#undef CURRENT_FILE_ID
#define CURRENT_FILE_ID FID_Git_Job_hunting_portfolio_piece_JobHunting_Plugins_Effekseer_Source_Effekseer_Public_EffekseerAlphaBlendType_h

// ********** Begin Enum EEffekseerAlphaBlendType **************************************************
#define FOREACH_ENUM_EEFFEKSEERALPHABLENDTYPE(op) \
	op(EEffekseerAlphaBlendType::Opacity) \
	op(EEffekseerAlphaBlendType::Blend) \
	op(EEffekseerAlphaBlendType::Add) \
	op(EEffekseerAlphaBlendType::Sub) \
	op(EEffekseerAlphaBlendType::Mul) 

enum class EEffekseerAlphaBlendType : uint8;
template<> struct TIsUEnumClass<EEffekseerAlphaBlendType> { enum { Value = true }; };
template<> EFFEKSEER_API UEnum* StaticEnum<EEffekseerAlphaBlendType>();
// ********** End Enum EEffekseerAlphaBlendType ****************************************************

PRAGMA_ENABLE_DEPRECATION_WARNINGS
