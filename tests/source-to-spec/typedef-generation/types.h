#ifndef TYPES_H
#define TYPES_H

/**
 * @defgroup TypesAPI Types API
 * @brief This is the Types API.
 */

/**
 * @file
 * @ingroup TypesAPI
 */

/**
 * @brief A widget size in application-defined units.
 */
typedef unsigned int widget_size_t;

/**
 * @brief A widget handle.
 */
typedef struct widget *widget_handle;

/**
 * @brief A named tag enum with a same-named typedef alias.
 */
typedef enum tagged_enum {
  /**
   * @brief Brief TAGGED_ENUM_A.
   */
  TAGGED_ENUM_A
} tagged_enum;

/**
 * @brief Handles a widget event.
 *
 * @param arg is the argument of the handler.
 */
typedef void ( *widget_handler )( int arg );
#endif
