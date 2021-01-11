/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `job_data`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `job_data` (
  `id` binary(16) NOT NULL DEFAULT (uuid_to_bin(uuid(),1)),
  `job_id` binary(16) NOT NULL,
  `schema_path` varchar(128) NOT NULL,
  `type` varchar(32) NOT NULL,
  `present` tinyint(1) NOT NULL DEFAULT '0',
  `format` varchar(64) DEFAULT NULL,
  `filename` varchar(128) DEFAULT NULL,
  `data` longblob,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modified_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `job_data_id_key` (`job_id`),
  CONSTRAINT `job_data_ibfk_1` FOREIGN KEY (`job_id`) REFERENCES `jobs` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `jobs`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jobs` (
  `id` binary(16) NOT NULL DEFAULT (uuid_to_bin(uuid(),1)),
  `user_id` binary(16) NOT NULL,
  `system_id` binary(16) NOT NULL,
  `definition` json NOT NULL,
  `status` enum('created','queued','complete','error') DEFAULT 'created',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modified_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `jobs_user_id_key` (`user_id`),
  CONSTRAINT `jobs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=COMPRESSED;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `schema_migrations`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schema_migrations` (
  `version` varchar(255) COLLATE latin1_bin NOT NULL,
  PRIMARY KEY (`version`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `systems`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `systems` (
  `id` binary(16) NOT NULL DEFAULT (uuid_to_bin(uuid(),1)),
  `user_id` binary(16) NOT NULL,
  `name` varchar(128) NOT NULL,
  `definition` json NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modified_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `system_user_name_key` (`user_id`,`name`),
  KEY `systems_user_id_key` (`user_id`),
  CONSTRAINT `systems_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=COMPRESSED;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` binary(16) NOT NULL DEFAULT (uuid_to_bin(uuid(),1)),
  `auth0_id` varchar(32) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth0_id_key` (`auth0_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=COMPRESSED;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'spi_data'
--
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`select_objects`@`localhost` FUNCTION `check_job_queued`(binid binary(16)) RETURNS tinyint(1)
    READS SQL DATA
    COMMENT 'Check, from a job data id, if a job is queued or complete'
begin
    return (select status != 'created' from jobs where id = (
      select job_id from job_data where id = binid));
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`select_objects`@`localhost` FUNCTION `check_users_job`(auth0id varchar(32), jobid char(36)) RETURNS tinyint(1)
    READS SQL DATA
    COMMENT 'Check if a job exists and belongs to the user'
begin
    return exists(select 1 from jobs where id = uuid_to_bin(jobid, 1)
                                       and user_id = get_user_binid(auth0id));
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`select_objects`@`localhost` FUNCTION `check_users_job_data`(auth0id varchar(32), jobid char(36), dataid char(36)) RETURNS tinyint(1)
    READS SQL DATA
    COMMENT 'Check if a job exists and belongs to the user'
begin
    return exists(
      select 1 from jobs where user_id = get_user_binid(auth0id)
        and id = uuid_to_bin(jobid, 1)
        and id = (select job_id from job_data where id = uuid_to_bin(dataid, 1)));
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`select_objects`@`localhost` FUNCTION `check_users_system`(auth0id varchar(32), systemid char(36)) RETURNS tinyint(1)
    READS SQL DATA
    COMMENT 'Check if the system exists and belongs to user'
begin
    return exists(select 1 from systems where id = uuid_to_bin(systemid, 1)
                                          and user_id = get_user_binid(auth0id));
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`select_objects`@`localhost` FUNCTION `does_user_exist`(auth0id varchar(32)) RETURNS tinyint(1)
    READS SQL DATA
    COMMENT 'Check if a user exists or not'
begin
    return exists(select 1 from users where auth0_id = auth0id);
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`select_objects`@`localhost` FUNCTION `get_user_binid`(auth0id varchar(32)) RETURNS binary(16)
    READS SQL DATA
    COMMENT 'Get the binary id of a user'
begin
    return (select id from users where auth0_id = auth0id);
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`select_objects`@`localhost` FUNCTION `get_user_id`(auth0id varchar(32)) RETURNS char(36) CHARSET utf8mb4
    READS SQL DATA
    COMMENT 'Get the id of a user'
begin
    return (select bin_to_uuid(id, 1) from users where auth0_id = auth0id);
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`select_objects`@`localhost` FUNCTION `job_dataobj_func`(jobid binary(16)) RETURNS json
    READS SQL DATA
    COMMENT 'Get the data objects as json for the job'
begin
    return (select json_arrayagg(json_object(
      'id', bin_to_uuid(id, 1), 'schema_path', schema_path, 'type', type, 'filename', filename,
      'data_format', format, 'present', present, 'created_at', created_at, 'modified_at', modified_at)
    ) from job_data where job_id = jobid);
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`select_objects`@`localhost` FUNCTION `job_status_func`(jobid binary(16)) RETURNS varchar(32) CHARSET utf8mb4
    READS SQL DATA
    COMMENT 'Get the status of a job'
begin
    declare status varchar(32);
    declare allnamed boolean;
    set status = (select jobs.status from jobs where id = jobid);

    if status = 'created' then
      set allnamed = (
        select bit_and(present) from job_data where job_id = jobid
      ) = 1;
      if allnamed then
        return 'prepared';
      else
        return 'incomplete';
      end if;
    end if;
    return status;
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`select_objects`@`localhost` FUNCTION `job_status_transition`(jobid binary(16)) RETURNS timestamp
    READS SQL DATA
    COMMENT 'Get the last transition time of the status'
begin
    declare status varchar(32);
    set status = (select jobs.status from jobs where id = jobid);

    if status = 'created' then
      return ifnull(
        (select max(modified_at) from job_data where job_id = jobid),
        (select created_at from jobs where id = jobid)
      );
    else
      return (select modified_at from jobs where id = jobid);
    end if;
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `add_example_data`()
    MODIFIES SQL DATA
begin
  CALL _add_example_data_0;
  CALL _add_example_data_1;
  CALL _add_example_data_2;
end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`update_objects`@`localhost` PROCEDURE `add_job_data`(auth0id varchar(32), jobid char(36), dataid char(36),
                          fname varchar(128), format varchar(64), newdata longblob)
    MODIFIES SQL DATA
    COMMENT 'Adds data for a job'
begin
    declare binid binary(16) default (uuid_to_bin(dataid, 1));
    declare allowed boolean default (check_users_job_data(auth0id, jobid, dataid));
    declare queued boolean default (check_job_queued(binid));

    if allowed then
      if queued then
        signal sqlstate '42000' set message_text = 'Job already queued',
        mysql_errno = 1348;
      else
        update job_data set filename = fname, data = newdata, format = format, present = true where id = binid;
      end if;
    else
      signal sqlstate '42000' set message_text = 'Job data upload denied',
      mysql_errno = 1142;
    end if;
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`insert_objects`@`localhost` PROCEDURE `create_job`(auth0id varchar(32), system_id char(36), definition json,
                        data_items json)
    MODIFIES SQL DATA
    COMMENT 'Create a new job'
begin
    declare sysid binary(16) default (uuid_to_bin(system_id, 1));
    declare jobid char(36) default (uuid());
    declare binid binary(16) default (uuid_to_bin(jobid, 1));
    declare userid binary(16) default (get_user_binid(auth0id));
    declare allowed boolean default (check_users_system(auth0id, system_id));

    if allowed then
      insert into jobs (id, user_id, system_id, definition) values (
        binid, userid, sysid, definition);
      insert into job_data (job_id, schema_path, type)
      select binid, jv.schema_path, jv.type from json_table(data_items, '$[*]' columns (
        schema_path varchar(128) path '$.schema_path' error on empty error on error,
        type varchar(32) path '$.type' error on empty error on error)) as jv;
      select jobid as job_id;
    else
      signal sqlstate '42000' set message_text = 'Job creation denied',
        mysql_errno = 1142;
    end if;
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`insert_objects`@`localhost` PROCEDURE `create_system`(auth0id varchar(32), name varchar(128), system_def JSON)
    MODIFIES SQL DATA
    COMMENT 'Create a new system'
begin
    declare sysid char(36) default (uuid());
    declare binid binary(16) default (uuid_to_bin(sysid, 1));
    insert into systems (id, user_id, name, definition) values (
      binid, get_user_binid(auth0id), name, system_def);
    select sysid as system_id;
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`insert_objects`@`localhost` PROCEDURE `create_user_if_not_exists`(in auth0id varchar(32))
    MODIFIES SQL DATA
    COMMENT 'Creates a user if nonexistent and returns the user id'
begin
    declare userid binary(16);
    if not does_user_exist(auth0id) then
      set userid = uuid_to_bin(uuid(), 1);
      insert into users (id, auth0_id) values (userid, auth0id);
      select bin_to_uuid(userid, 1) as user_id;
    else
      select get_user_id(auth0id) as user_id;
    end if;
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`delete_objects`@`localhost` PROCEDURE `delete_job`(auth0id varchar(32), jobid char(36))
    MODIFIES SQL DATA
    COMMENT 'Delete a job'
begin
    declare binid binary(16) default (uuid_to_bin(jobid, 1));
    declare allowed boolean default (check_users_job(auth0id, jobid));

    if allowed then
      delete from jobs where id = binid;
    else
      signal sqlstate '42000' set message_text = 'Job deletion denied',
        mysql_errno = 1142;
    end if;
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`delete_objects`@`localhost` PROCEDURE `delete_system`(auth0id varchar(32), systemid char(36))
    MODIFIES SQL DATA
    COMMENT 'Delete a system'
begin
    declare binid binary(16) default (uuid_to_bin(systemid, 1));
    declare allowed boolean default (check_users_system(auth0id, systemid));
    declare uid binary(16) default get_user_binid(auth0id);

    if allowed then
      delete from systems where id = binid;
    else
      signal sqlstate '42000' set message_text = 'Deleting system not allowed',
        mysql_errno = 1142;
    end if;
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`delete_objects`@`localhost` PROCEDURE `delete_user_by_auth0id`(in auth0id varchar(32))
    MODIFIES SQL DATA
    COMMENT 'Delete a user by auth0 ID'
begin
    declare userid binary(16);
    if does_user_exist(auth0id) then
      delete from users where auth0_id = auth0id;
    else
      signal sqlstate '42000' set message_text = 'User does not exist',
        mysql_errno = 1142;
    end if;
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`select_objects`@`localhost` PROCEDURE `get_job`(auth0id varchar(32), job_id char(36))
    READS SQL DATA
    COMMENT 'Read a jobs metadata'
begin
    declare binid binary(16) default (uuid_to_bin(job_id, 1));
    declare allowed boolean default (check_users_job(auth0id, job_id));

    if allowed then
      select bin_to_uuid(id, 1) as job_id, bin_to_uuid(user_id, 1) as user_id,
      bin_to_uuid(system_id, 1) as system_id, definition, created_at, modified_at,
      json_object('status', job_status_func(binid), 'last_change', job_status_transition(binid)) as status,
      job_dataobj_func(binid) as data_objects
      from jobs where id = binid;
    else
      signal sqlstate '42000' set message_text = 'Job inaccessible',
        mysql_errno = 1142;
    end if;
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`select_objects`@`localhost` PROCEDURE `get_job_data`(auth0id varchar(32), jobid char(36), dataid char(36))
    READS SQL DATA
    COMMENT 'Read the data for a single job data id'
begin
    declare binid binary(16) default (uuid_to_bin(dataid, 1));
    declare allowed boolean default (check_users_job_data(auth0id, jobid, dataid));

    if allowed then
      select bin_to_uuid(id, 1) as id, bin_to_uuid(job_id, 1) as job_id,
      schema_path, type, filename, data, present, format as data_format, created_at, modified_at
      from job_data where id = binid;
    else
      signal sqlstate '42000' set message_text = 'Job data retrieval denied',
        mysql_errno = 1142;
    end if;
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`select_objects`@`localhost` PROCEDURE `get_job_status`(auth0id varchar(32), jobid char(36))
    READS SQL DATA
    COMMENT 'Get status of a job'
begin
    declare binid binary(16) default (uuid_to_bin(jobid, 1));
    declare allowed boolean default (check_users_job(auth0id, jobid));

    if allowed then
      select job_status_func(binid) as status,
      job_status_transition(binid) as last_change;
    else
      signal sqlstate '42000' set message_text = 'Job status inaccessible',
        mysql_errno = 1142;
    end if;
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`select_objects`@`localhost` PROCEDURE `get_system`(auth0id varchar(32), systemid char(36))
    READS SQL DATA
    COMMENT 'Get the definition for a system'
begin
    declare binid binary(16) default (uuid_to_bin(systemid, 1));
    declare allowed boolean default (check_users_system(auth0id, systemid));

    if allowed then
      select bin_to_uuid(id, 1) as system_id, bin_to_uuid(user_id, 1) as user_id,
      name, definition, created_at, modified_at from systems where id = binid;
    else
      signal sqlstate '42000' set message_text = 'System inaccessible',
        mysql_errno = 1142;
    end if;
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`select_objects`@`localhost` PROCEDURE `get_user`(in auth0id varchar(32))
    READS SQL DATA
    COMMENT 'Get a user by auth0 id'
begin
    if does_user_exist(auth0id) then
      select bin_to_uuid(id, 1) as user_id, auth0_id, created_at from users where auth0_id = auth0id;
    else
      signal sqlstate '42000' set message_text = 'User does not exist',
        mysql_errno = 1142;
    end if;
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`select_objects`@`localhost` PROCEDURE `list_jobs`(auth0id varchar(32))
    READS SQL DATA
    COMMENT 'Get metadata for all jobs'
begin
    select bin_to_uuid(id, 1) as job_id, bin_to_uuid(user_id, 1) as user_id,
           bin_to_uuid(system_id, 1) as system_id, definition, created_at, modified_at,
           json_object('status', job_status_func(id), 'last_change', job_status_transition(id)) as status,
           job_dataobj_func(id) as data_objects
      from jobs where check_users_job(auth0id, bin_to_uuid(id, 1));
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`select_objects`@`localhost` PROCEDURE `list_systems`(auth0id varchar(32))
    READS SQL DATA
    COMMENT 'List all user systems'
begin
    select bin_to_uuid(id, 1) as system_id, bin_to_uuid(user_id, 1) as user_id,
           name, definition, created_at, modified_at from systems
     where user_id = get_user_binid(auth0id);
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`update_objects`@`localhost` PROCEDURE `queue_job`(auth0id varchar(32), jobid char(36))
    MODIFIES SQL DATA
    COMMENT 'Change the status to queued if allowed'
begin
    declare binid binary(16) default (uuid_to_bin(jobid, 1));
    declare allowed boolean default (check_users_job(auth0id, jobid));
    declare status varchar(32) default (job_status_func(binid));

    if allowed then
      if status = 'prepared' or status = 'queued' then
        update jobs set status = 'queued' where id = binid;
      elseif status = 'incomplete' then
        signal sqlstate '42000' set message_text = 'Missing required job data',
        mysql_errno = 1054;
      else
        signal sqlstate '42000' set message_text = 'Job already computed',
        mysql_errno = 1062;
      end if;
    else
      signal sqlstate '42000' set message_text = 'Job queueing denied',
      mysql_errno = 1142;
    end if;
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `remove_example_data`()
    MODIFIES SQL DATA
begin
  CALL _remove_example_data_0;
  CALL _remove_example_data_1;
end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`update_objects`@`localhost` PROCEDURE `update_system`(auth0id varchar(32), systemid char(36), system_def JSON)
    MODIFIES SQL DATA
    COMMENT 'Update a system definition'
begin
    declare binid binary(16) default (uuid_to_bin(systemid, 1));
    declare allowed boolean default (check_users_system(auth0id, systemid));
    declare uid binary(16) default get_user_binid(auth0id);

    if allowed then
      update systems set definition = system_def where id = binid;
    else
      signal sqlstate '42000' set message_text = 'Updating system not allowed',
        mysql_errno = 1142;
    end if;
  end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `_add_example_data_0`()
    MODIFIES SQL DATA
    COMMENT 'Add example data to the database'
begin
  set @userid = uuid_to_bin('17fbf1c6-34bd-11eb-af43-f4939feddd82', 1);
  set @otheruser = uuid_to_bin('972084d4-34cd-11eb-8f13-f4939feddd82', 1);
  set @sysid = uuid_to_bin('6b61d9ac-2e89-11eb-be2a-4dc7a6bcd0d9', 1);
  set @othersysid = uuid_to_bin('6513485a-34cd-11eb-8f13-f4939feddd82', 1);
  set @extime = timestamp('2020-12-01 01:23');
  set @sysdef = '{
       "name": "Test PV System",
       "latitude": 33.98,
       "longitude": -115.323,
       "elevation": 2300,
       "inverters": [
         {
           "name": "Inverter 1",
           "make_model": "ABB__MICRO_0_25_I_OUTD_US_208__208V_",
           "inverter_parameters": {
             "Pso": 2.08961,
             "Paco": 250,
             "Pdco": 259.589,
             "Vdco": 40,
             "C0": -4.1e-05,
             "C1": -9.1e-05,
             "C2": 0.000494,
             "C3": -0.013171,
             "Pnt": 0.075
           },
           "losses": {},
           "arrays": [
             {
               "name": "Array 1",
               "make_model": "Canadian_Solar_Inc__CS5P_220M",
               "albedo": 0.2,
               "modules_per_string": 7,
               "strings": 5,
               "tracking": {
                 "tilt": 20.0,
                 "azimuth": 180.0
               },
               "temperature_model_parameters": {
                 "u_c": 29.0,
                 "u_v": 0.0,
                 "eta_m": 0.1,
                 "alpha_absorption": 0.9
               },
               "module_parameters": {
                 "alpha_sc": 0.004539,
                 "gamma_ref": 1.2,
                 "mu_gamma": -0.003,
                 "I_L_ref": 5.11426,
                 "I_o_ref": 8.10251e-10,
                 "R_sh_ref": 381.254,
                 "R_s": 1.06602,
                 "R_sh_0": 400.0,
                 "cells_in_series": 96
               }
             }
           ]
         }
       ]
     }';

  insert into users (auth0_id, id, created_at) values (
    'auth0|5fa9596ccf64f9006e841a3a', @userid, @extime
  ),(
    'auth0|invalid', @otheruser, @extime
    );
  insert into systems (id, user_id, name, definition, created_at, modified_at) values (
    @sysid, @userid, 'Test PV System', @sysdef, @extime, @extime
  ),(
    @othersysid, @otheruser, 'Other system', '{}', @extime, @extime
    );
end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `_add_example_data_1`()
    MODIFIES SQL DATA
begin
  set @jobid = uuid_to_bin('e1772e64-43ac-11eb-92c2-f4939feddd82', 1);
  set @otherjobid = uuid_to_bin('7f13ab34-43ad-11eb-80a2-f4939feddd82', 1);
  set @jobdataid0 = uuid_to_bin('ecaa5a40-43ac-11eb-a75d-f4939feddd82', 1);
  set @jobdataid1 = uuid_to_bin('f9ef0c00-43ac-11eb-8931-f4939feddd82', 1);
  set @userid = uuid_to_bin('17fbf1c6-34bd-11eb-af43-f4939feddd82', 1);
  set @otheruser = uuid_to_bin('972084d4-34cd-11eb-8f13-f4939feddd82', 1);
  set @sysid = uuid_to_bin('6b61d9ac-2e89-11eb-be2a-4dc7a6bcd0d9', 1);
  set @othersysid = uuid_to_bin('6513485a-34cd-11eb-8f13-f4939feddd82', 1);
  set @extime = timestamp('2020-12-11 19:52');
  set @modtime = timestamp('2020-12-11 20:00');

  set @sysjson = (select cast(definition as json) from systems where id = @sysid);
  set @jobparams = '{"parameters": {
      "system_id": "6b61d9ac-2e89-11eb-be2a-4dc7a6bcd0d9",
      "time_parameters": {
        "start": "2020-01-01T00:00:00+00:00",
        "end": "2020-12-31T23:59:59+00:00",
        "step": "15:00",
        "timezone": "UTC"
      },
      "weather_granularity": "array",
      "job_type": {
        "compare": "predicted and actual performance",
        "performance_granularity": "inverter"
      },
      "irradiance_type": "poa",
      "temperature_type": "module"}}';
  -- odd annoying way to make sure system def is also json
  set @jobjson = json_set(@jobparams, '$.system_definition', json_value(@sysjson, '$' returning json));

  insert into jobs (id, user_id, system_id, definition, status, created_at, modified_at) values (
    @jobid, @userid, @sysid, @jobjson, 'created', @extime, @extime), (
      @otherjobid, @otheruser, @othersysid, @jobjson, 'created', @extime, @extime);
  insert into job_data (id, job_id, schema_path, type, created_at, modified_at) values (
    @jobdataid0, @jobid, '/inverters/0/arrays/0', 'original weather data', @extime, @extime), (
      @jobdataid1, @jobid, '/inverters/0', 'actual performance data', @extime, @extime);
  update job_data set present = true, data = 'binary data blob', format = 'application/vnd.apache.arrow.file', filename = 'inverter_0_performance.arrow', modified_at = @modtime  where id = @jobdataid1;
end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `_add_example_data_2`()
    MODIFIES SQL DATA
    COMMENT 'Add real arrow data for job'
begin
  set @jobdataid1 = uuid_to_bin('f9ef0c00-43ac-11eb-8931-f4939feddd82', 1);
  set @modtime = timestamp('2020-12-11 20:00');
  update job_data set
    present = true,
    format = 'application/vnd.apache.arrow.file',
    filename = 'inverter_0_performance.arrow',
    modified_at = @modtime ,
    data = from_base64('
QVJST1cxAAD/////gAIAABAAAAAAAAoADgAGAAUACAAKAAAAAAEEABAAAAAAAAoADAAAAAQACAAK
AAAAvAEAAAQAAAABAAAADAAAAAgADAAEAAgACAAAAAgAAAAQAAAABgAAAHBhbmRhcwAAhwEAAHsi
aW5kZXhfY29sdW1ucyI6IFtdLCAiY29sdW1uX2luZGV4ZXMiOiBbXSwgImNvbHVtbnMiOiBbeyJu
YW1lIjogInRpbWUiLCAiZmllbGRfbmFtZSI6ICJ0aW1lIiwgInBhbmRhc190eXBlIjogImRhdGV0
aW1ldHoiLCAibnVtcHlfdHlwZSI6ICJkYXRldGltZTY0W25zXSIsICJtZXRhZGF0YSI6IHsidGlt
ZXpvbmUiOiAiVVRDIn19LCB7Im5hbWUiOiAicGVyZm9ybWFuY2UiLCAiZmllbGRfbmFtZSI6ICJw
ZXJmb3JtYW5jZSIsICJwYW5kYXNfdHlwZSI6ICJpbnQ2NCIsICJudW1weV90eXBlIjogImludDY0
IiwgIm1ldGFkYXRhIjogbnVsbH1dLCAiY3JlYXRvciI6IHsibGlicmFyeSI6ICJweWFycm93Iiwg
InZlcnNpb24iOiAiMi4wLjAifSwgInBhbmRhc192ZXJzaW9uIjogIjEuMS40In0AAgAAAFQAAAAE
AAAAxP///wAAAQIQAAAAJAAAAAQAAAAAAAAACwAAAHBlcmZvcm1hbmNlAAgADAAIAAcACAAAAAAA
AAFAAAAAEAAUAAgABgAHAAwAAAAQABAAAAAAAAEKEAAAACAAAAAEAAAAAAAAAAQAAAB0aW1lAAAA
AAgADAAGAAgACAAAAAAAAwAEAAAAAwAAAFVUQwD/////yAAAABQAAAAAAAAADAAYAAYABQAIAAwA
DAAAAAADBAAcAAAAUAAAAAAAAAAAAAAADAAcABAABAAIAAwADAAAAGgAAAAcAAAAFAAAAAIAAAAA
AAAAAAAAAAQABAAEAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACcAAAAAAAAAKAAAAAAA
AAAAAAAAAAAAACgAAAAAAAAAJAAAAAAAAAAAAAAAAgAAAAIAAAAAAAAAAAAAAAAAAAACAAAAAAAA
AAAAAAAAAAAAEAAAAAAAAAAEIk0YYECCEAAAgAAAirk1muUVAKBC6nud5RUAAAAAABAAAAAAAAAA
BCJNGGBAgg0AAAATAAEAgAEAAAAAAAAAAAAAAAAAAAD/////AAAAABAAAAAMABQABgAIAAwAEAAM
AAAAAAAEAEAAAAAoAAAABAAAAAEAAACQAgAAAAAAANAAAAAAAAAAUAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAoADAAAAAQACAAKAAAAvAEAAAQAAAABAAAADAAAAAgADAAEAAgACAAAAAgAAAAQAAAABgAA
AHBhbmRhcwAAhwEAAHsiaW5kZXhfY29sdW1ucyI6IFtdLCAiY29sdW1uX2luZGV4ZXMiOiBbXSwg
ImNvbHVtbnMiOiBbeyJuYW1lIjogInRpbWUiLCAiZmllbGRfbmFtZSI6ICJ0aW1lIiwgInBhbmRh
c190eXBlIjogImRhdGV0aW1ldHoiLCAibnVtcHlfdHlwZSI6ICJkYXRldGltZTY0W25zXSIsICJt
ZXRhZGF0YSI6IHsidGltZXpvbmUiOiAiVVRDIn19LCB7Im5hbWUiOiAicGVyZm9ybWFuY2UiLCAi
ZmllbGRfbmFtZSI6ICJwZXJmb3JtYW5jZSIsICJwYW5kYXNfdHlwZSI6ICJpbnQ2NCIsICJudW1w
eV90eXBlIjogImludDY0IiwgIm1ldGFkYXRhIjogbnVsbH1dLCAiY3JlYXRvciI6IHsibGlicmFy
eSI6ICJweWFycm93IiwgInZlcnNpb24iOiAiMi4wLjAifSwgInBhbmRhc192ZXJzaW9uIjogIjEu
MS40In0AAgAAAFQAAAAEAAAAxP///wAAAQIQAAAAJAAAAAQAAAAAAAAACwAAAHBlcmZvcm1hbmNl
AAgADAAIAAcACAAAAAAAAAFAAAAAEAAUAAgABgAHAAwAAAAQABAAAAAAAAEKEAAAACAAAAAEAAAA
AAAAAAQAAAB0aW1lAAAAAAgADAAGAAgACAAAAAAAAwAEAAAAAwAAAFVUQwCwAgAAQVJST1cx
')
   where id = @jobdataid1;
end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `_remove_example_data_0`()
    MODIFIES SQL DATA
    COMMENT 'Remove example data from the database'
begin
  set @userid = uuid_to_bin('17fbf1c6-34bd-11eb-af43-f4939feddd82', 1);
  set @sysid = uuid_to_bin('6b61d9ac-2e89-11eb-be2a-4dc7a6bcd0d9', 1);
  set @othersysid = uuid_to_bin('6513485a-34cd-11eb-8f13-f4939feddd82', 1);
  set @otheruser = uuid_to_bin('972084d4-34cd-11eb-8f13-f4939feddd82', 1);

  delete from systems where id = @sysid;
  delete from systems where id = @othersysid;
  delete from users where id = @userid;
  delete from users where id = @otheruser;
end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `_remove_example_data_1`()
    MODIFIES SQL DATA
begin
  set @jobid = uuid_to_bin('e1772e64-43ac-11eb-92c2-f4939feddd82', 1);
  set @otherjobid = uuid_to_bin('7f13ab34-43ad-11eb-80a2-f4939feddd82', 1);
  delete from jobs where id = @jobid;
  delete from jobs where id = @otherjobid;
end ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed

--
-- Dbmate schema migrations
--

LOCK TABLES `schema_migrations` WRITE;
INSERT INTO `schema_migrations` (version) VALUES
  ('20201130184500'),
  ('20201130190000'),
  ('20201130190100'),
  ('20201202162400'),
  ('20201208224427'),
  ('20201214175739'),
  ('20201221161319'),
  ('20210107162707');
UNLOCK TABLES;
