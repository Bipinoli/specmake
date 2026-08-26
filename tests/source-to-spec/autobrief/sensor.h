/**
 * @file
 *
 * @ingroup SensorAPI
 *
 * @brief This header file provides the sensor API.
 */

/**
 * @defgroup SensorAPI Sensor API
 *
 * @brief This group contains the sensor API.
 */

/**
 * Reads the sensor.  The caller owns the buffer.
 */
int sensor_read( void );

/**
 * @brief Resets the sensor.
 */
void sensor_reset( void );

void sensor_stop( void );
