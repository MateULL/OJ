-- MySQL schema for the OJ business tables.
-- Generated from the current Django models and migrations in backend/oj/migrations/.
-- Source of truth remains Django migrations; this file is a convenience DDL export.
--
-- Important:
-- 1. This file covers the `oj` app business tables only.
-- 2. Django built-in tables such as `auth_user`, `django_admin_log`,
--    `django_content_type`, `django_migrations`, and `django_session`
--    are not included here.
-- 3. Create those built-in tables with `python manage.py migrate`,
--    or make sure they already exist before applying the foreign keys below.

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS `oj_problem` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(200) NOT NULL,
  `display_number` INT UNSIGNED NULL,
  `description` LONGTEXT NOT NULL,
  `difficulty` VARCHAR(16) NOT NULL DEFAULT '',
  `sample_input` LONGTEXT NOT NULL,
  `sample_output` LONGTEXT NOT NULL,
  `time_limit_ms` INT UNSIGNED NOT NULL DEFAULT 1000,
  `memory_limit_mb` INT UNSIGNED NOT NULL DEFAULT 128,
  `judge_mode` VARCHAR(32) NOT NULL DEFAULT 'standard',
  `is_public` BOOL NOT NULL DEFAULT 1,
  `created_at` DATETIME(6) NOT NULL,
  `updated_at` DATETIME(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oj_problem_display_number_uniq` (`display_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `oj_testcase` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `problem_id` BIGINT NOT NULL,
  `input_path` VARCHAR(500) NOT NULL,
  `output_path` VARCHAR(500) NOT NULL,
  `sort_order` INT UNSIGNED NOT NULL DEFAULT 1,
  `score` INT UNSIGNED NOT NULL DEFAULT 0,
  `is_hidden` BOOL NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_testcase_problem_order` (`problem_id`, `sort_order`),
  KEY `oj_testcase_problem_id_fk` (`problem_id`),
  CONSTRAINT `oj_testcase_problem_id_fk` FOREIGN KEY (`problem_id`)
    REFERENCES `oj_problem` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `oj_problemsamplecase` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `problem_id` BIGINT NOT NULL,
  `sort_order` INT UNSIGNED NOT NULL DEFAULT 1,
  `input_file` VARCHAR(100) NOT NULL,
  `output_file` VARCHAR(100) NOT NULL,
  `input_text` LONGTEXT NOT NULL,
  `output_text` LONGTEXT NOT NULL,
  `created_at` DATETIME(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_problem_sample_case_order` (`problem_id`, `sort_order`),
  KEY `oj_problemsamplecase_problem_id_fk` (`problem_id`),
  CONSTRAINT `oj_problemsamplecase_problem_id_fk` FOREIGN KEY (`problem_id`)
    REFERENCES `oj_problem` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `oj_submission` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT NOT NULL,
  `problem_id` BIGINT NOT NULL,
  `language` VARCHAR(32) NOT NULL DEFAULT 'cpp17',
  `source_code` LONGTEXT NOT NULL,
  `status` VARCHAR(20) NOT NULL DEFAULT 'QUEUED',
  `final_verdict` VARCHAR(20) NULL,
  `total_time_ms` INT UNSIGNED NOT NULL DEFAULT 0,
  `max_memory_kb` INT UNSIGNED NOT NULL DEFAULT 0,
  `compile_log` LONGTEXT NOT NULL,
  `submitted_at` DATETIME(6) NOT NULL,
  `judged_at` DATETIME(6) NULL,
  PRIMARY KEY (`id`),
  KEY `oj_submission_status_idx` (`status`),
  KEY `oj_submission_final_verdict_idx` (`final_verdict`),
  KEY `oj_submission_submitted_at_idx` (`submitted_at`),
  KEY `oj_submission_problem_id_fk` (`problem_id`),
  KEY `oj_submission_user_id_fk` (`user_id`),
  KEY `idx_submission_queue` (`status`, `submitted_at`),
  KEY `idx_submission_problem` (`problem_id`, `submitted_at`),
  KEY `idx_submission_user` (`user_id`, `submitted_at`),
  CONSTRAINT `oj_submission_problem_id_fk` FOREIGN KEY (`problem_id`)
    REFERENCES `oj_problem` (`id`) ON DELETE CASCADE,
  CONSTRAINT `oj_submission_user_id_fk` FOREIGN KEY (`user_id`)
    REFERENCES `auth_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `oj_submissioncaseresult` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `submission_id` BIGINT NOT NULL,
  `test_case_id` BIGINT NOT NULL,
  `verdict` VARCHAR(20) NOT NULL,
  `time_used_ms` INT UNSIGNED NOT NULL DEFAULT 0,
  `memory_used_kb` INT UNSIGNED NOT NULL DEFAULT 0,
  `message` LONGTEXT NOT NULL,
  `created_at` DATETIME(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_submission_case_result` (`submission_id`, `test_case_id`),
  KEY `oj_submissioncaseresult_submission_id_fk` (`submission_id`),
  KEY `oj_submissioncaseresult_test_case_id_fk` (`test_case_id`),
  CONSTRAINT `oj_submissioncaseresult_submission_id_fk` FOREIGN KEY (`submission_id`)
    REFERENCES `oj_submission` (`id`) ON DELETE CASCADE,
  CONSTRAINT `oj_submissioncaseresult_test_case_id_fk` FOREIGN KEY (`test_case_id`)
    REFERENCES `oj_testcase` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
