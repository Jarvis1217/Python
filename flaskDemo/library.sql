/*
Navicat MySQL Data Transfer

Source Server         : library
Source Server Version : 80022
Source Host           : localhost:3306
Source Database       : library

Target Server Type    : MYSQL
Target Server Version : 80022
File Encoding         : 65001

Date: 2021-03-21 00:12:35
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for userinfo
-- ----------------------------
DROP TABLE IF EXISTS `userinfo`;
CREATE TABLE `userinfo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `userName` varchar(255) NOT NULL,
  `userPasswd` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of userinfo
-- ----------------------------
