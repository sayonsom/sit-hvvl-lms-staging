-- Seed data for High Voltage Engineering course
-- Run AFTER CreateInitialTables.sql

-- Instructor
INSERT INTO Instructors (instructor_id, name, email, organization, city, profile_picture, linkedin, website, biography)
VALUES (1, 'Dr. Anurag Sharma, Dr. Dhivya Sampath Kumar', 'anurag.sharma@newcastle.ac.uk',
        'Newcastle University, Singapore Institute of Technology', 'Singapore',
        'https://res.cloudinary.com/dti7egpsg/image/upload/v1695741601/SIT%20Align/SIT_logo_2_llcb1k.png',
        'https://example.com/', 'https://example.com/', 'Instructors for High Voltage Engineering')
ON CONFLICT (email) DO NOTHING;

-- Course
INSERT INTO Courses (course_id, title, description, course_image, enrollment_status,
                     enrollment_begin_date, enrollment_end_date, session_start_date, session_end_date,
                     course_webpage, syllabus_pdf_link, instructor_id)
VALUES (2, 'High Voltage Engineering',
        '6-Credit Core Course offered as a part of three-year B.Eng program in Electrical Power Engineering',
        'https://res.cloudinary.com/dti7egpsg/image/upload/v1706098910/SIT%20Align/HV_Course_Icon_ic0kak.webp',
        'By Invite Only', '2024-06-01', '2025-12-31', '2024-06-01', '2025-12-31',
        'https://www.singaporetech.edu.sg/undergraduate-programmes/electrical-power-engineering',
        'https://example.com/', 1)
ON CONFLICT DO NOTHING;

-- Reset sequence so course_id=2 is valid
SELECT setval('courses_course_id_seq', (SELECT COALESCE(MAX(course_id), 1) FROM courses));
SELECT setval('instructors_instructor_id_seq', (SELECT COALESCE(MAX(instructor_id), 1) FROM instructors));

-- 5 Modules
INSERT INTO Modules (module_id, course_id, title, description, theory, concept, fun_fact, interactive_file,
                     attachment_1_link, attachment_2_link, attachment_3_link,
                     video_link_1, video_link_2, plottingexperimentconfig, InteractiveConfig)
VALUES
('95ae078a-b69a-416c-bdf5-ee744bcf3b79', 2,
 'Ferranti Effect',
 'Discover the fascinating Ferranti effect, a phenomenon that defies intuition and showcases the complex behavior of electricity in long transmission lines.',
 'exp3_ferranti_effect/Ferranti Effect Lab CAA 8 Feb 24.md',
 'The Ferranti effect is a phenomenon that occurs in long transmission lines, particularly in power systems with high voltage and low load. It is named after Sebastian Ziani de Ferranti, an electrical engineer who first described it. The effect is characterized by a voltage rise at the receiving end of the transmission line, which can be higher than the voltage at the sending end.',
 'Did you know that the Ferranti effect was accidentally discovered in 1890 during the installation of the world''s first high-voltage AC transmission line between Deptford and London?',
 'exp3_ferranti_effect/ferranti_effect.glb', NULL, NULL, NULL,
 'https://youtu.be/7JNJ7xOXlgM?si=WtBRW3S72DZN7AKy', NULL,
 'exp3_ferranti_effect/exp3_ferranti_config.json', NULL),

('4e0fb4de-77c9-499e-913b-5d175ceb6ab5', 2,
 'Impulse Voltage Generator',
 'Prepare to delve into the world of high-voltage engineering with impulse voltage generators, the ultimate tools for testing the resilience of electrical equipment against lightning strikes and power surges.',
 'exp1_impulse_voltage_generator/ImpulseVoltageTheory_v1.md',
 'An impulse voltage generator is a device used to generate high-voltage, short-duration impulses for testing the insulation and dielectric strength of electrical equipment. It consists of a charging circuit, a capacitor bank for energy storage, and a switching mechanism (usually a spark gap) to rapidly discharge the stored energy.',
 'The impulse voltage generator has a fascinating origin story that dates back to the early 20th century.',
 'exp1_impulse_voltage_generator/impulse_voltage_generator.glb', NULL, NULL, NULL,
 'https://youtu.be/3UTMNrraACk?si=M34HvRD6UCPQYvNG', NULL,
 'exp1_impulse_voltage_generator/exp1_impulse_voltage_generator_config.json', NULL),

('d5c97a6b-98a0-4d44-b0c1-a47c86c80910', 2,
 '3-Stage Cockroft-Walton',
 'Embark on a journey through the ingenious world of high-voltage generation with the Cockcroft-Walton voltage multiplier.',
 'exp2_3stage_cockroft_walton/3 Stage Cockroft Walton Voltage Multiplier.md',
 'The Cockcroft-Walton voltage multiplier is a circuit that generates high DC voltages from a low-voltage AC or pulsed DC input. It consists of a cascade of capacitors and diodes arranged in a ladder-like structure.',
 'This circuit is commonly used in applications such as particle accelerators, X-ray machines, and high voltage power supplies.',
 'exp2_3stage_cockroft_walton/cockroft-walton.glb', NULL, NULL, NULL,
 'https://youtu.be/QAAngb2XeOc?si=JeZ1VY5KjQdHyj2y', NULL,
 'exp2_3stage_cockroft_walton/exp2_cockroft_walton.json', NULL),

('fe91690b-514f-40f0-a581-c363f710db5a', 2,
 'Partial Discharge',
 'Partial Discharge Experiment focuses on detecting and analyzing small electrical discharges in insulation systems that can lead to major failures.',
 'exp4_partial_discharge/Partial Discharge Lab Manual.md',
 'Partial discharge (PD) refers to localized dielectric breakdowns within a small portion of an insulation system under high voltage stress, without completely bridging the electrodes.',
 'The phenomenon is sometimes referred to as "electrical treeing" because under high voltage stress, the discharges can create microscopic pathways in the insulation that resemble the branches of a tree.',
 'exp4_partial_discharge/partialDischarge.glb', NULL, NULL, NULL,
 'https://youtu.be/MNmaGPTBDIo?si=lVGy18n-aLhrBho9', NULL,
 'exp4_partial_discharge/exp4_partial_discharge_config.json', NULL),

('d35deeab-df2b-455f-9977-d7f7508cd9be', 2,
 'Transient Voltage Recovery',
 'Transient Voltage Recovery explores the rapid restoration of voltage levels after disturbances in power systems.',
 'exp5_transient_recovery_voltage/Transient Voltage Lab Manual.md',
 'Transient Recovery Voltage (TRV) is the voltage that appears across a circuit breaker immediately after it interrupts a fault, caused by the inductive energy in the system.',
 'During the testing of high-voltage circuit breakers for TRV performance, engineers sometimes create artificial lightning to simulate extreme fault conditions.',
 'exp5_transient_recovery_voltage/highvoltage_trv.gltf', NULL, NULL, NULL,
 'https://youtu.be/GgPGaLXlJfk?si=Dxu-oCJU4TjLgSvQ', NULL,
 'exp5_transient_recovery_voltage/exp5_transientvoltage_config.json', NULL)
ON CONFLICT DO NOTHING;

-- Assignments (one per module)
INSERT INTO Assignments (assignment_id, module_id, title, description, due_date) VALUES
(11, '95ae078a-b69a-416c-bdf5-ee744bcf3b79', 'Default Assignment', NULL, '2025-12-31'),
(12, '4e0fb4de-77c9-499e-913b-5d175ceb6ab5', 'Default Assignment', NULL, '2025-12-31'),
(13, 'd5c97a6b-98a0-4d44-b0c1-a47c86c80910', 'Default Assignment', NULL, '2025-12-31'),
(14, 'fe91690b-514f-40f0-a581-c363f710db5a', 'Default Assignment', NULL, '2025-12-31'),
(23, 'd35deeab-df2b-455f-9977-d7f7508cd9be', 'Default Assignment', NULL, '2025-12-31')
ON CONFLICT DO NOTHING;

SELECT setval('assignments_assignment_id_seq', (SELECT COALESCE(MAX(assignment_id), 1) FROM assignments));

-- Questions
INSERT INTO Questions (question_id, assignment_id, question_text, question_type, correct_option_id) VALUES
-- Ferranti Effect (assignment 11)
(17, 11, 'What is the Ferranti Effect in transmission lines?', 'multiple_choice', 65),
(18, 11, 'In which type of transmission lines is the Ferranti Effect more pronounced?', 'multiple_choice', 71),
(19, 11, 'What causes the Ferranti Effect?', 'multiple_choice', 73),
(20, 11, 'What is the primary consequence of the Ferranti Effect?', 'multiple_choice', 79),
(21, 11, 'How can the Ferranti Effect be mitigated?', 'multiple_choice', 81),
(22, 11, 'Which of the following best describes the Ferranti Effect?', 'multiple_choice', 86),
(23, 11, 'At what condition does the Ferranti Effect occur in a transmission line?', 'multiple_choice', 89),
(24, 11, 'Which of the following components in a transmission line is most associated with the Ferranti Effect?', 'multiple_choice', 95),
(25, 11, 'What is the typical voltage profile of a transmission line experiencing the Ferranti Effect?', 'multiple_choice', 99),
(26, 11, 'How does the length of the transmission line affect the Ferranti Effect?', 'multiple_choice', 102),
-- Impulse Voltage Generator (assignment 12)
(27, 12, 'What is an Impulse Voltage Generator used for?', 'multiple_choice', 108),
(28, 12, 'What is the primary component of an Impulse Voltage Generator?', 'multiple_choice', 110),
(29, 12, 'What is the typical shape of the waveform produced by an Impulse Voltage Generator?', 'multiple_choice', 115),
(30, 12, 'What is the primary application of Impulse Voltage Generators?', 'multiple_choice', 119),
(31, 12, 'How can the performance of an Impulse Voltage Generator be improved?', 'multiple_choice', 124),
-- Cockcroft-Walton (assignment 13)
(32, 13, 'What is the purpose of a Cockcroft-Walton generator?', 'multiple_choice', 126),
(33, 13, 'How many diodes are used in a 3-stage Cockcroft-Walton generator?', 'multiple_choice', 130),
(34, 13, 'What is the main advantage of using a Cockcroft-Walton generator?', 'multiple_choice', 134),
(35, 13, 'What is the main disadvantage of a Cockcroft-Walton generator?', 'multiple_choice', 140),
(36, 13, 'What type of components are used to construct a Cockcroft-Walton generator?', 'multiple_choice', 142),
(37, 13, 'What is the typical application of a Cockcroft-Walton generator?', 'multiple_choice', 148),
(38, 13, 'How can the output voltage of a Cockcroft-Walton generator be increased?', 'multiple_choice', 149),
-- Partial Discharge (assignment 14)
(39, 14, 'What is partial discharge (PD)?', 'multiple_choice', 154),
(40, 14, 'Which type of partial discharge is commonly observed near sharp conductor edges under high voltage conditions?', 'multiple_choice', 158),
(41, 14, 'What is the primary cause of surface discharge in insulation?', 'multiple_choice', 161),
(42, 14, 'Void discharge typically occurs in which part of the high voltage system?', 'multiple_choice', 167),
(43, 14, 'Which method is NOT commonly used for detecting partial discharge?', 'multiple_choice', 172),
(44, 14, 'During partial discharge testing, what is the purpose of gradually increasing the test voltage?', 'multiple_choice', 175),
(45, 14, 'What type of signal is generated in a cable during partial discharge?', 'multiple_choice', 178),
(46, 14, 'In partial discharge testing on cables, what does the time of arrival of a pulse help to determine?', 'multiple_choice', 182),
(47, 14, 'Which factor does NOT affect signal attenuation in partial discharge testing?', 'multiple_choice', 187),
(48, 14, 'What is the main consequence of void discharge within insulating material cavities?', 'multiple_choice', 189),
(49, 14, 'What is the role of multiple sensors in partial discharge localization?', 'multiple_choice', 194),
(50, 14, 'What type of partial discharge is most likely to cause immediate insulation failure?', 'multiple_choice', 199),
-- TRV (assignment 23)
(107, 23, 'What is the purpose of a TRV withstand test on a circuit breaker?', 'multiple_choice', 425),
(108, 23, 'Which component has the most influence on TRV in a transmission network?', 'multiple_choice', 430),
(109, 23, 'What parameter is critical when selecting a breaker for high RRRV conditions?', 'multiple_choice', 436),
(110, 23, 'What does a successful TRV withstand test indicate?', 'multiple_choice', 437),
(111, 23, 'Which protection method helps reduce TRV impact on breakers?', 'multiple_choice', 443),
(112, 23, 'Which TRV characteristic directly influences breaker dielectric recovery?', 'multiple_choice', 447),
(113, 23, 'What might result from inadequate TRV control in high-voltage circuits?', 'multiple_choice', 449),
(114, 23, 'How is TRV affected by the circuit''s natural frequency?', 'multiple_choice', 455),
(115, 23, 'Which testing standard applies to TRV for DC breakers?', 'multiple_choice', 460),
(116, 23, 'What is the primary factor in designing breakers for varying TRV levels?', 'multiple_choice', 462)
ON CONFLICT DO NOTHING;

SELECT setval('questions_question_id_seq', (SELECT COALESCE(MAX(question_id), 1) FROM questions));

-- Options (4 per question)
INSERT INTO Options (option_id, question_id, option_text) VALUES
-- Ferranti Effect Q17-26
(65,17,'Voltage rise at the receiving end'),(66,17,'Voltage drop at the sending end'),(67,17,'Voltage drop at the receiving end'),(68,17,'Voltage rise at the sending end'),
(69,18,'Short transmission lines'),(70,18,'Medium transmission lines'),(71,18,'Long transmission lines'),(72,18,'Very short transmission lines'),
(73,19,'Capacitive reactance'),(74,19,'Inductive reactance'),(75,19,'Magnetic flux'),(76,19,'Electric field'),
(77,20,'Voltage drop at the sending end'),(78,20,'Increased power loss'),(79,20,'Voltage rise at the receiving end'),(80,20,'Constant current flow'),
(81,21,'By adding series inductance'),(82,21,'By adding series resistance'),(83,21,'By adding shunt capacitance'),(84,21,'By adding shunt inductance'),
(85,22,'Reduction in voltage'),(86,22,'Voltage rise at the receiving end'),(87,22,'Constant voltage'),(88,22,'Constant current'),
(89,23,'Under light load or no load'),(90,23,'Under heavy load'),(91,23,'Under short circuit conditions'),(92,23,'Under balanced load'),
(93,24,'Resistors'),(94,24,'Inductors'),(95,24,'Capacitors'),(96,24,'Transformers'),
(97,25,'Constant voltage throughout'),(98,25,'Voltage rise at the sending end'),(99,25,'Voltage rise at the receiving end'),(100,25,'Voltage drop at the receiving end'),
(101,26,'The effect decreases with length'),(102,26,'The effect increases with length'),(103,26,'The effect is independent of length'),(104,26,'The effect fluctuates with length'),
-- Impulse Voltage Q27-31
(105,27,'Generating steady DC voltage'),(106,27,'Generating steady AC voltage'),(107,27,'Generating high-frequency signals'),(108,27,'Generating high voltage pulses'),
(109,28,'Resistor'),(110,28,'Capacitor'),(111,28,'Inductor'),(112,28,'Transformer'),
(113,29,'Sine wave'),(114,29,'Square wave'),(115,29,'Impulse wave'),(116,29,'Triangle wave'),
(117,30,'Telecommunication'),(118,30,'Medical equipment'),(119,30,'High voltage testing'),(120,30,'Signal processing'),
(121,31,'By increasing the capacitance'),(122,31,'By increasing the inductance'),(123,31,'By improving the insulation'),(124,31,'By using faster switches'),
-- Cockcroft-Walton Q32-38
(125,32,'To generate high current'),(126,32,'To generate high voltage'),(127,32,'To generate high frequency'),(128,32,'To generate steady DC voltage'),
(129,33,'3'),(130,33,'6'),(131,33,'9'),(132,33,'12'),
(133,34,'High efficiency'),(134,34,'Simple design'),(135,34,'Low cost'),(136,34,'Compact size'),
(137,35,'Large size'),(138,35,'Voltage drop'),(139,35,'Complex design'),(140,35,'Ripple voltage'),
(141,36,'Resistors and capacitors'),(142,36,'Diodes and capacitors'),(143,36,'Transistors and inductors'),(144,36,'Transformers and resistors'),
(145,37,'Low voltage testing'),(146,37,'High current testing'),(147,37,'Power amplification'),(148,37,'Radiation therapy'),
(149,38,'By increasing the number of stages'),(150,38,'By decreasing the load'),(151,38,'By increasing the frequency'),(152,38,'By increasing the input voltage'),
-- Partial Discharge Q39-50
(153,39,'A complete breakdown of insulation'),(154,39,'A localized electrical discharge in a compromised insulating medium'),(155,39,'A phenomenon only in low voltage systems'),(156,39,'An issue that only affects the outer surface'),
(157,40,'Surface discharge'),(158,40,'Corona discharge'),(159,40,'Void discharge'),(160,40,'Internal discharge'),
(161,41,'Poor maintenance and high humidity'),(162,41,'Overvoltage'),(163,41,'Low operating temperature'),(164,41,'Direct exposure to sunlight'),
(165,42,'In the air surrounding the conductor'),(166,42,'On the surface of the insulator'),(167,42,'Within insulating material cavities'),(168,42,'At the interface between two dielectrics'),
(169,43,'Acoustic Detection'),(170,43,'Transient Earth Voltage (TEV) Detection'),(171,43,'High Frequency Current Transformer (HFCT)'),(172,43,'Optical Fiber Detection'),
(173,44,'To simulate operating conditions'),(174,44,'To ensure safety'),(175,44,'To induce partial discharges'),(176,44,'To test mechanical strength'),
(177,45,'Low-frequency pulses'),(178,45,'High-frequency pulses'),(179,45,'Continuous waves'),(180,45,'Low amplitude ripples'),
(181,46,'The cable''s operating voltage'),(182,46,'The exact location of the partial discharge'),(183,46,'The material of the insulation'),(184,46,'The type of discharge'),
(185,47,'Type of cable'),(186,47,'Length of the cable'),(187,47,'Operating temperature'),(188,47,'Loading condition'),
(189,48,'It leads to the formation of treeing channels'),(190,48,'It reduces the conductivity'),(191,48,'It improves insulation efficiency'),(192,48,'It eliminates surface discharge'),
(193,49,'To ensure redundancy'),(194,49,'To pinpoint the location of insulation voids'),(195,49,'To measure the voltage level'),(196,49,'To increase the noise'),
(197,50,'Corona discharge'),(198,50,'Surface discharge'),(199,50,'Void discharge'),(200,50,'Edge discharge'),
-- TRV Q107-116
(425,107,'To verify the dielectric strength of the breaker'),(426,107,'To ensure the thermal stability'),(427,107,'To check for mechanical endurance'),(428,107,'To validate the timing accuracy'),
(429,108,'The grounding reactor'),(430,108,'The line inductance'),(431,108,'The load capacitance'),(432,108,'The system neutral earthing'),
(433,109,'Rated voltage of the breaker'),(434,109,'Breaking time of the breaker'),(435,109,'Current rating of the breaker'),(436,109,'Dielectric strength of the breaker'),
(437,110,'That the breaker can interrupt fault current safely'),(438,110,'That the breaker can withstand over-voltages'),(439,110,'That the breaker will not re-ignite'),(440,110,'That the breaker will trip instantly'),
(441,111,'Shunt capacitors'),(442,111,'Series reactors'),(443,111,'Surge arresters'),(444,111,'Current limiters'),
(445,112,'Peak voltage magnitude'),(446,112,'Frequency of oscillations'),(447,112,'Rate of Rise of Recovery Voltage (RRRV)'),(448,112,'Current waveform'),
(449,113,'Frequent restrikes'),(450,113,'Increased arc duration'),(451,113,'Voltage collapse'),(452,113,'Loss of synchronism'),
(453,114,'It is inversely proportional'),(454,114,'It has no effect'),(455,114,'It directly correlates'),(456,114,'It is dependent on breaker type'),
(457,115,'IEC 61643'),(458,115,'IEC 60076'),(459,115,'IEEE C37.14'),(460,115,'IEC 62271-100'),
(461,116,'Contact gap distance'),(462,116,'Insulation material'),(463,116,'Arc extinction medium'),(464,116,'Trip coil design')
ON CONFLICT DO NOTHING;

SELECT setval('options_option_id_seq', (SELECT COALESCE(MAX(option_id), 1) FROM options));
