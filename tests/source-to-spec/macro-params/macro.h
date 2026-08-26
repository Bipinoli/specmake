/**
 * @file
 *
 * @ingroup MacroAPI
 *
 * @brief This header file provides the macro API.
 */

/**
 * @defgroup MacroAPI Macro API
 *
 * @brief This group contains the macro API.
 */

/**
 * @brief Logs the message.
 *
 * @param level is the log level.
 */
#define MACRO_LOG( level, ... ) macro_log( level, __VA_ARGS__ )

/**
 * @brief Returns the larger operand.
 *
 * @param a,b are the two operands.
 */
#define MACRO_MAX( a, b ) ( ( a ) > ( b ) ? ( a ) : ( b ) )

/**
 * @brief Returns the sum.
 *
 * @param b is the second operand.
 * @param a is the first operand.
 */
#define MACRO_ADD( a, b ) ( ( a ) + ( b ) )

/**
 * @brief Returns the smaller operand.
 */
#define MACRO_MIN( a, b ) ( ( a ) < ( b ) ? ( a ) : ( b ) )

/**
 * @brief Is the empty statement.
 */
#define MACRO_NOP() do { } while ( 0 )

/**
 * @brief Is the maximum count.
 */
#define MACRO_COUNT 32

/**
 * @brief Stores the value.
 *
 * @param value is the value to store.
 * @param slot is the slot to store the value in.
 */
void macro_store( int value );

/**
 * @brief Sets the size.
 *
 * @param width is the width.
 * @param height is the height.
 */
void macro_set_size( int, int );
