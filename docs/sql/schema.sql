-- 이 파일은 MySQL 기준 테이블 생성 스키마를 정의하는 파일

CREATE TABLE IF NOT EXISTS cafe (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS menu (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cafe_menu_rank (
  cafe_id BIGINT NOT NULL,
  menu_id BIGINT NOT NULL,
  count INT NOT NULL,
  rank INT NOT NULL,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (cafe_id, menu_id),
  CONSTRAINT fk_cmr_cafe FOREIGN KEY (cafe_id) REFERENCES cafe(id),
  CONSTRAINT fk_cmr_menu FOREIGN KEY (menu_id) REFERENCES menu(id)
);

CREATE TABLE IF NOT EXISTS menu_daily_stats (
  stat_date DATE NOT NULL,
  cafe_id BIGINT NOT NULL,
  menu_id BIGINT NOT NULL,
  mention_count INT NOT NULL,
  non_ad_count INT NOT NULL,
  ad_ratio DECIMAL(5,4) NOT NULL,
  trend_score DECIMAL(10,4) NOT NULL,
  popularity_score DECIMAL(10,4) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (stat_date, cafe_id, menu_id),
  CONSTRAINT fk_mds_cafe FOREIGN KEY (cafe_id) REFERENCES cafe(id),
  CONSTRAINT fk_mds_menu FOREIGN KEY (menu_id) REFERENCES menu(id)
);

CREATE TABLE IF NOT EXISTS menu_alias (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  menu_id BIGINT NOT NULL,
  alias_name VARCHAR(255) NOT NULL UNIQUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_ma_menu FOREIGN KEY (menu_id) REFERENCES menu(id)
);

CREATE TABLE IF NOT EXISTS menu_candidate (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  cafe_id BIGINT NOT NULL,
  candidate_name VARCHAR(255) NOT NULL,
  mention_count INT NOT NULL,
  first_seen_at DATETIME NOT NULL,
  last_seen_at DATETIME NOT NULL,
  status VARCHAR(50) NOT NULL,
  CONSTRAINT fk_mc_cafe FOREIGN KEY (cafe_id) REFERENCES cafe(id)
);
