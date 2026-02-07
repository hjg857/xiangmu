<template>
  <div class="report-container" ref="reportContainer">
    <!-- 顶部操作栏 -->
    <div class="report-header no-print">
      <div class="header-left">
        <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
        <h1>评估报告</h1>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="downloadPDF" :loading="downloading" :icon="Download">
          {{ downloading ? '生成中...' : '下载PDF' }}
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <p>正在加载报告数据...</p>
    </div>

    <!-- 报告内容 -->
    <div v-else-if="reportData && reportData.school_name" class="report-content" ref="reportContent">
      <!-- 报告封面/标题 -->
      <div class="report-title-section">
        <h1 class="main-title">{{ reportData.school_name }}数据文化成熟度评估报告</h1>
        <p class="report-date">报告生成时间：{{ formatDate(reportData.report_date) }}</p>
      </div>

      <!-- 报告说明 -->
      <div class="report-intro">
        <p>本报告旨在帮助您全面了解学校数据文化建设情况。数据文化是指学校在数据使用和管理方面的制度、规范、实践和价值观的集合；而数据文化成熟度则是学校在数据使用、管理和价值实现方面的成熟程度。平台基于学校填报的多维度数据，通过科学的评估规则，并辅助于DeepSeek大模型进行智能评估，准确识别学校数据文化的建设水平与现实问题，以促进学校数据使用、管理和价值实现，推动学校数据治理能力的提升。本报告包括以下五个核心分析维度：</p>
        <ol>
          <li><strong>数据素养</strong>：评估学校管理者、教师和学生在数据应用方面的综合能力，包括数据意识与思维、数据知识与技能、数据伦理与隐私等，为数据文化的落地提供核心人才支撑。</li>
          <li><strong>数据制度</strong>：评估学校在组织架构、人员配备与管理规范方面的制度化水平，包括数据组织机构、数据人员配备、数据管理文件等，为学校数据文化的有序发展提供制度依据。</li>
          <li><strong>数据行为</strong>：评估数据在工作、学习与决策中的实际应用情况，包括学生数据行为、教师数据行为、数据应用成效等。</li>
          <li><strong>数据资产</strong>：评估学校对数据资源的认知水平、积累规模等内容，包括数据资产意识、数据资产总量等。</li>
          <li><strong>数据技术</strong>：评估学校在数据采集、存储、处理与安全保障方面的技术支撑能力，包括数据硬件设施、数据系统平台、数据安全合规与认证等，为数据文化提供可靠的底层支撑。</li>
        </ol>
      </div>

      <!-- 第一部分：学校数据文化评估概况 -->
      <section class="report-section">
        <h2 class="section-title">
          <el-icon><DataAnalysis /></el-icon>
          学校数据文化评估概况
        </h2>
        
        <p class="section-summary">
          学校数据文化整体处于{{ reportData.maturity_level }}（{{ reportData.total_score_percent?.toFixed(2) }}分）。
          其中数据素养（{{ dimensionScores.literacy?.toFixed(2) }}分）
          {{ getPerformanceText(dimensionScores.literacy) }}，
          数据制度（{{ dimensionScores.institution?.toFixed(2) }}分）
          {{ getPerformanceText(dimensionScores.institution) }}，
          数据行为（{{ dimensionScores.behavior?.toFixed(2) }}分）
          {{ getPerformanceText(dimensionScores.behavior) }}，
          数据资产（{{ dimensionScores.asset?.toFixed(2) }}分）
          {{ getPerformanceText(dimensionScores.asset) }}，
          数据技术（{{ dimensionScores.technology?.toFixed(2) }}分）
          {{ getPerformanceText(dimensionScores.technology) }}。
        </p>

        <!-- 总分和等级展示 -->
        <div class="overview-scores">
          <div class="score-card total">
            <span class="label">学校数据文化得分</span>
            <span class="value">{{ reportData.total_score?.toFixed(2) }}分</span>
          </div>
          <div class="score-card level">
            <span class="label">学校数据文化等级</span>
            <span class="value">{{ getLevelNumber(reportData.maturity_level) }} {{ reportData.maturity_level }}</span>
          </div>
        </div>

        <!-- 概况图表区域 -->
        <div class="overview-chart-container">
          <div class="overview-left">
            <div class="dimension-list">
              <div class="dimension-header">
                <span >总体概况</span>
                <span class="total-score-badge">{{ Math.round(reportData.total_score || 0) }}分</span>
                <span class="level-badge">{{ reportData.maturity_level }}</span>
              </div>
              <div class="dimension-item" v-for="(item, key) in dimensionList" :key="key">
                <span class="dim-name">{{ item.name }}</span>
                <span class="dim-score">{{ item.score?.toFixed(1) }}分</span>
              </div>
            </div>
          </div>
          <div class="overview-right">
            <div ref="overviewChart" class="chart-box" style="height: 350px;"></div>
          </div>
        </div>

        <!-- AI评估建议 -->
        <div class="ai-suggestion">
          <h4>评估建议：</h4>
          <p>{{ reportData.suggestions?.overall || '暂无建议' }}</p>
        </div>

        <div class="evaluation-note">
          <h4>评估说明：</h4>
          <p>最终计算真实得分的评分区间为[0,5]，目前分为四个等级：初始级（0~1.5）、成长级（1.5~3.0）、成熟级（3.0~4.0）、创新级（4.0~5.0）。</p>
        </div>
      </section>

      <!-- 第二部分：学校数据素养分析 -->
      <section class="report-section page-break">
        <h2 class="section-title">
          <el-icon><Reading /></el-icon>
          学校数据素养分析
        </h2>

        <!-- 计分规则说明 -->
        <div class="scoring-rules">
          <h4><el-icon><InfoFilled /></el-icon> 计分规则说明</h4>
          <p>数据素养维度总权重为 <strong>0.3543</strong>，下设三个二级指标：</p>
          <ul>
            <li><strong>A1 教师数据素养</strong>（权重 0.3748）：包含数据意识与思维、知识与技能、评价与交流、应用与创新、伦理与隐私5个观测点。</li>
            <li><strong>A2 管理者数据素养</strong>（权重 0.3443）：包含数据意识与思维、知识与技能、评价与交流、应用与创新、伦理与隐私5个观测点。</li>
            <li><strong>A3 学生数据素养</strong>（权重 0.2809）：包含数据意识与思维、知识与技能、评价与交流、应用与创新、伦理与隐私5个观测点。</li>
          </ul>
          <p class="rule-note">注：观测点采用5点量表计分，最终得分经过标准化处理转换为百分制。</p>
        </div>

        <p class="section-summary">
          学校数据素养得分为{{ dimensionScores.literacy?.toFixed(1) }}分。
          其中，教师数据素养得分为{{ secondaryScores.A1?.toFixed(1) }}分，
          管理者数据素养得分为{{ secondaryScores.A2?.toFixed(1) }}分，
          学生数据素养得分为{{ secondaryScores.A3?.toFixed(1) }}分。
          具体情况如下：
        </p>

        <!-- 三个群体得分展示 -->
        <div class="literacy-scores">
          <div class="literacy-score-card teacher">
            <span class="score">{{ secondaryScores.A1?.toFixed(1) }}分</span>
            <span class="label">教师平均分</span>
          </div>
          <div class="literacy-score-card manager">
            <span class="score">{{ secondaryScores.A2?.toFixed(1) }}分</span>
            <span class="label">管理者平均分</span>
          </div>
          <div class="literacy-score-card student">
            <span class="score">{{ secondaryScores.A3?.toFixed(1) }}分</span>
            <span class="label">学生平均分</span>
          </div>
        </div>

        <!-- 参评人数 -->
        <div class="participant-info">
          <span>教师参评人数：{{ reportData.participant_counts?.teacher || 0 }}人</span>
          <span>管理者参评人数：{{ reportData.participant_counts?.manager || 0 }}人</span>
          <span>学生参评人数：{{ reportData.participant_counts?.student || 0 }}人</span>
        </div>

        <!-- 三个雷达图 -->
        <div class="literacy-radar-section">
          <h4>各群体数据素养雷达图</h4>
          <div class="radar-charts-row">
            <div class="radar-chart-item">
              <div ref="teacherRadarChart" class="chart-box" style="height: 280px;"></div>
            </div>
            <div class="radar-chart-item">
              <div ref="managerRadarChart" class="chart-box" style="height: 280px;"></div>
            </div>
            <div class="radar-chart-item">
              <div ref="studentRadarChart" class="chart-box" style="height: 280px;"></div>
            </div>
          </div>
        </div>

        <!-- 综合对比柱状图 -->
        <div class="literacy-comparison-section">
          <h4>数据素养综合对比</h4>
          <div ref="literacyComparisonChart" class="chart-box" style="height: 350px;"></div>
        </div>

        <!-- AI评估建议 -->
        <div class="ai-suggestion">
          <h4>评估建议：</h4>
          <p>{{ reportData.suggestions?.literacy || '暂无建议' }}</p>
        </div>
      </section>

      <!-- 第三部分：学校数据制度分析 -->
      <section class="report-section page-break">
        <h2 class="section-title">
          <el-icon><Document /></el-icon>
          学校数据制度分析
        </h2>

        <!-- 计分规则说明 -->
        <div class="scoring-rules">
          <h4><el-icon><InfoFilled /></el-icon> 计分规则说明</h4>
          <p>数据制度维度总权重为 <strong>0.1578</strong>，下设三个二级指标：</p>
          <ul>
            <li><strong>B1 数据组织机构</strong>（权重 0.3599）：
              <ul>
                <li>B11 数据领导/工作小组（满分10分）：设立计10分，未设立计0分。</li>
                <li>B12 数据组织运行情况（满分10分）：按近5年相关会议/活动次数计分（≤5次计3分，5-15次计6分，>15次计10分）。</li>
              </ul>
            </li>
            <li><strong>B2 数据人员配备</strong>（权重 0.4131）：
              <ul>
                <li>B21 数据专职/兼职管理人员（满分20分）：根据是否配备、人数及职责明确情况计分。</li>
                <li>B22 数据人员进修与培训情况（满分30分）：根据是否参与、频次及证书获得情况计分。</li>
              </ul>
            </li>
            <li><strong>B3 数据管理文件</strong>（权重 0.2270）：
              <ul>
                <li>B31 数据管理制度类文件（满分40分）：根据文件出台情况及质量（DeepSeek评估）计分。</li>
                <li>B32 数据实践指导类文件（满分40分）：根据文件出台情况及质量（DeepSeek评估）计分。</li>
              </ul>
            </li>
          </ul>
        </div>

        <p class="section-summary">
          学校数据制度得分为{{ dimensionScores.institution?.toFixed(1) }}分。
          其中，数据组织机构得分{{ secondaryScores.B1?.toFixed(1) }}分，
          数据人员配备得分{{ secondaryScores.B2?.toFixed(1) }}分，
          数据管理文件得分{{ secondaryScores.B3?.toFixed(1) }}分。
          具体情况如下：
        </p>

        <!-- 数据组织机构 -->
        <div class="institution-card">
          <div class="card-header">
            <span class="card-title">数据组织机构：{{ secondaryScores.B1?.toFixed(0) }}分</span>
          </div>
          <div class="card-content">
            <div class="info-item">
              <span class="info-label">数据领导/工作小组</span>
              <span class="info-value">学校{{ institutionDetails.has_leadership_group ? '已设立' : '未设立' }}数据领导/工作小组。</span>
            </div>
            <div class="info-item">
              <span class="info-label">数据组织运行情况</span>
              <span class="info-value">近5年，学校组织开展数据相关会议、活动{{ institutionDetails.meeting_activity_count || 0 }}次。</span>
            </div>
          </div>
        </div>

        <!-- 数据人员配备 -->
        <div class="institution-card">
          <div class="card-header">
            <span class="card-title">数据人员配备：{{ secondaryScores.B2?.toFixed(0) }}分</span>
          </div>
          <div class="card-content">
            <div class="info-item">
              <span class="info-label">数据专职/兼职管理人员</span>
              <div class="info-value">
                <p>1. 配备专职人员{{ institutionDetails.fulltime_staff_count || 0 }}位，兼职人员{{ institutionDetails.parttime_staff_count || 0 }}位。</p>
                <p>2. 学校专职人员{{ institutionDetails.has_clear_responsibilities ? '已有' : '暂无' }}明确职务。</p>
              </div>
            </div>
            <div class="info-item">
              <span class="info-label">数据人员进修与培训情况</span>
              <div class="info-value">
                <p>1. 学校近5年参与数据相关培训{{ institutionDetails.training_count || 0 }}次。</p>
                <p>2. 相关人员获得证书{{ (institutionDetails.national_cert_count || 0) + (institutionDetails.provincial_cert_count || 0) + (institutionDetails.city_cert_count || 0) }}份。</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 数据管理文件 -->
        <div class="institution-card">
          <div class="card-header">
            <span class="card-title">数据管理文件：{{ secondaryScores.B3?.toFixed(0) }}分</span>
          </div>
          <div class="card-content">
            <div class="info-item">
              <span class="info-label">数据管理制度类文件</span>
              <div class="info-value">
                <p>1. 学校发布{{ getTotalManagementDocs() }}份制度文件。</p>
                <div v-if="institutionDetails.management_doc_analysis" class="llm-analysis">
                  <p>2. 大模型文件质量分析：</p>
                  <div class="analysis-content">{{ institutionDetails.management_doc_analysis }}</div>
                </div>
              </div>
            </div>
            <div class="info-item">
              <span class="info-label">数据实践指导类文件</span>
              <div class="info-value">
                <p>1. 学校发布{{ getTotalPracticeDocs() }}份数据指导相关文件。</p>
                <div v-if="institutionDetails.practice_doc_analysis" class="llm-analysis">
                  <p>2. 大模型文件质量分析：</p>
                  <div class="analysis-content">{{ institutionDetails.practice_doc_analysis }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI评估建议 -->
        <div class="ai-suggestion">
          <h4>评估建议：</h4>
          <p>{{ reportData.suggestions?.institution || '暂无建议' }}</p>
        </div>
      </section>

      <!-- 第四部分：学校数据行为分析 -->
      <section class="report-section page-break">
        <h2 class="section-title">
          <el-icon><TrendCharts /></el-icon>
          学校数据行为分析
        </h2>

        <!-- 计分规则说明 -->
        <div class="scoring-rules">
          <h4><el-icon><InfoFilled /></el-icon> 计分规则说明</h4>
          <p>数据行为维度总权重为 <strong>0.1930</strong>，下设两个二级指标：</p>
          <ul>
            <li><strong>C1 数据行为监测</strong>（权重 0.4679）：
              <ul>
                <li>C11 教师数据行为（满分10分）：按人均登录频次计分（≤200次计3分，200-300次计6分，>300次计10分）。</li>
                <li>C12 学生数据行为（满分10分）：按人均登录频次计分（≤100次计3分，100-200次计6分，>200次计10分）。</li>
                <li>C13 管理者数据行为（满分10分）：按人均登录频次计分（≤200次计3分，200-300次计6分，>300次计10分）。</li>
              </ul>
            </li>
            <li><strong>C2 数据应用成效</strong>（权重 0.5321）：
              <ul>
                <li>C21 数据应用特色成果（满分60分）：包含论文、著作、典型案例、荣誉奖励等，按数量及级别计分。</li>
                <li>C22 数据应用社会影响（满分50分）：包含媒体报道、经验交流、参观学习等，按次数及级别计分。</li>
                <li>C23 应用效果主观评价（满分85分）：基于问卷调查，评估师生对数据应用成效的满意度。</li>
              </ul>
            </li>
          </ul>
        </div>

        <p class="section-summary">
          学校数据行为得分为{{ dimensionScores.behavior?.toFixed(1) }}分。
          其中，数据行为监测得分{{ secondaryScores.C1?.toFixed(1) }}分，
          数据应用成效{{ secondaryScores.C2?.toFixed(1) }}分。
          具体情况如下：
        </p>

        <!-- 数据行为监测 -->
        <div class="behavior-card">
          <div class="card-header">
            <span class="card-title">数据行为监测：{{ secondaryScores.C1?.toFixed(0) }}分</span>
          </div>
          <div class="card-content">
            <div class="login-stats">
              <p>上1学年，全校教师登录数据相关平台的人均频次：{{ behaviorDetails.teacher_login_freq || 0 }}次</p>
              <p>上1学年，全校学生登录数据相关平台的人均频次：{{ behaviorDetails.student_login_freq || 0 }}次</p>
              <p>上1学年，全校管理者登录数据相关平台的人均频次：{{ behaviorDetails.manager_login_freq || 0 }}次</p>
            </div>
            <div ref="behaviorBarChart" class="chart-box" style="height: 250px;"></div>
          </div>
        </div>

        <!-- 数据应用成效 -->
        <div class="behavior-card">
          <div class="card-header">
            <span class="card-title">数据应用成效：{{ secondaryScores.C2?.toFixed(0) }}分</span>
          </div>
          <div class="card-content">
            <div class="achievement-section">
              <h5>数据应用特色成果</h5>
              <p>出版论文{{ behaviorDetails.published_paper_count || 0 }}篇、著作{{ behaviorDetails.published_book_count || 0 }}部、典型案例{{ getTotalCases() }}个、获得奖励荣誉{{ getTotalAwards() }}个</p>
            </div>
            <div class="achievement-section">
              <h5>数据应用社会影响</h5>
              <p>学校被报道{{ getTotalMedia() }}次、参与经验交流{{ getTotalConference() }}次、参观学习{{ behaviorDetails.visit_count || 0 }}次</p>
            </div>
            <div class="achievement-section">
              <h5>应用效果主观评价</h5>
              <p>学校教师学生对数据应用成效的主观评价：</p>
              <div class="participant-info">
                <span>教师参评人数：{{ reportData.participant_counts?.teacher || 0 }}人</span>
                <span>学生参评人数：{{ reportData.participant_counts?.student || 0 }}人</span>
              </div>
              <div class="behavior-radar-row">
                <div ref="teacherEffectRadar" class="chart-box" style="height: 250px; flex: 1;"></div>
                <div ref="studentEffectRadar" class="chart-box" style="height: 250px; flex: 1;"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI评估建议 -->
        <div class="ai-suggestion">
          <h4>评估建议：</h4>
          <p>{{ reportData.suggestions?.behavior || '暂无建议' }}</p>
        </div>
      </section>

      <!-- 第五部分：学校数据资产分析 -->
      <section class="report-section page-break">
        <h2 class="section-title">
          <el-icon><Files /></el-icon>
          学校数据资产分析
        </h2>

        <!-- 计分规则说明 -->
        <div class="scoring-rules">
          <h4><el-icon><InfoFilled /></el-icon> 计分规则说明</h4>
          <p>数据资产维度总权重为 <strong>0.1549</strong>，下设两个二级指标：</p>
          <ul>
            <li><strong>D1 数据资产意识</strong>（权重 0.4795）：包含价值意识（20分）、应用意识（20分）、治理意识（30分），通过管理者问卷评估。</li>
            <li><strong>D2 数据资产积累</strong>（权重 0.5205）：
              <ul>
                <li>D21 数据资产总量（满分10分）：按累计存储总量计分（≤1TB计2分，1-5.5TB计4分，5.5-9TB计6分，>9TB计10分）。</li>
                <li>D22 人均数据资产量（满分10分）：按师生人均存储量计分（≤10GB计3分，10-20GB计6分，20-40GB计10分，>40GB计10分）。</li>
              </ul>
            </li>
          </ul>
        </div>

        <p class="section-summary">
          学校数据资产得分为{{ dimensionScores.asset?.toFixed(1) }}分。
          其中，数据资产意识得分{{ secondaryScores.D1?.toFixed(1) }}分，
          数据资产积累{{ secondaryScores.D2?.toFixed(1) }}分。
          具体情况如下：
        </p>

        <!-- 数据资产意识 -->
        <div class="asset-card">
          <div class="card-header">
            <span class="card-title">数据资产意识：{{ secondaryScores.D1?.toFixed(0) }}分</span>
            <span class="card-subtitle">其中{{ reportData.participant_counts?.manager || 0 }}名管理者参评</span>
          </div>
          <div class="card-content">
            <div ref="assetAwarenessRadar" class="chart-box" style="height: 300px;"></div>
          </div>
        </div>

        <!-- 数据资产积累 -->
        <div class="asset-card">
          <div class="card-header">
            <span class="card-title">数据资产积累：{{ secondaryScores.D2?.toFixed(0) }}分</span>
          </div>
          <div class="card-content">
            <div class="staff-info">
              <span>学校在职教师：{{ assetDetails.staff_count || 0 }}人</span>
              <span>学校学生人数：{{ assetDetails.student_count || 0 }}人</span>
            </div>
            <div class="asset-progress-section">
              <div class="progress-card">
                <div class="progress-header">
                  <span class="progress-title">D21 数据资产总量</span>
                </div>
                <div class="progress-value">{{ formatDataVolume(assetDetails.total_data_volume) }}</div>
                <div class="progress-label">累计数据存储总量</div>
                <el-progress 
                  :percentage="getVolumePercentage(assetDetails.total_data_volume, 5000)" 
                  :stroke-width="12"
                  :show-text="false"
                  color="#67c23a"
                />
                <div class="progress-range">
                  <span>0 GB</span>
                  <span>5000 GB</span>
                </div>
              </div>
              <div class="progress-card">
                <div class="progress-header">
                  <span class="progress-title">D22 人均数据资产量</span>
                </div>
                <div class="progress-value red">{{ getPerCapitaVolume() }} GB</div>
                <div class="progress-label">按师生人数平均</div>
                <el-progress 
                  :percentage="getVolumePercentage(parseFloat(getPerCapitaVolume()), 10)" 
                  :stroke-width="12"
                  :show-text="false"
                  color="#f56c6c"
                />
                <div class="progress-range">
                  <span>0 GB</span>
                  <span>10 GB</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI评估建议 -->
        <div class="ai-suggestion">
          <h4>评估建议：</h4>
          <p>{{ reportData.suggestions?.asset || '暂无建议' }}</p>
        </div>
      </section>

      <!-- 第六部分：学校数据技术分析 -->
      <section class="report-section page-break">
        <h2 class="section-title">
          <el-icon><Setting /></el-icon>
          学校数据技术分析
        </h2>

        <!-- 计分规则说明 -->
        <div class="scoring-rules">
          <h4><el-icon><InfoFilled /></el-icon> 计分规则说明</h4>
          <p>数据技术维度总权重为 <strong>0.1400</strong>，下设两个二级指标：</p>
          <ul>
            <li><strong>E1 数据基础设施</strong>（权重 0.5449）：
              <ul>
                <li>E11 数据硬件设施（满分30分）：根据独立数据中心建设标准及数字终端师生机比计分。</li>
                <li>E12 数据系统平台（满分10分）：建设数据治理平台计10分，否则计0分。</li>
              </ul>
            </li>
            <li><strong>E2 数据安保水平</strong>（权重 0.4551）：
              <ul>
                <li>E21 数据安全合规与认证（满分20分）：根据通过等保认定的平台数量及比例计分。</li>
                <li>E22 数据风险事件记录（满分0分）：发生数据风险事件扣10分，未发生不扣分。</li>
              </ul>
            </li>
          </ul>
        </div>

        <p class="section-summary">
          学校数据技术得分为{{ dimensionScores.technology?.toFixed(1) }}分。
          其中，数据基础设施得分{{ secondaryScores.E1?.toFixed(1) }}分，
          数据安保水平{{ secondaryScores.E2?.toFixed(1) }}分。
          具体情况如下：
        </p>

        <!-- 数据基础设施 -->
        <div class="tech-card">
          <div class="card-header">
            <span class="card-title">数据基础设施：{{ secondaryScores.E1?.toFixed(0) }}分</span>
          </div>
          <div class="card-content">
            <div class="info-item">
              <span class="info-label">数据硬件设施</span>
              <div class="info-value">
                <p>1. 学校{{ getDataCenterText() }}。</p>
                <p>2. 数字终端配备生机比为：{{ technologyDetails.student_device_ratio_display || '未填写' }}，师机比为{{ technologyDetails.teacher_device_ratio_display || '未填写' }}。</p>
              </div>
            </div>
            <div class="info-item">
              <span class="info-label">数据系统平台</span>
              <div class="info-value">
                <p>学校{{ technologyDetails.has_data_platform ? '建设有' : '暂未建设' }}数据治理平台，如数据中台、数据交换中心等。</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 数据安保水平 -->
        <div class="tech-card">
          <div class="card-header">
            <span class="card-title">数据安保水平：{{ secondaryScores.E2?.toFixed(0) }}分</span>
          </div>
          <div class="card-content">
            <div class="info-item">
              <span class="info-label">数据安全合规与认证</span>
              <div class="info-value">
                <p>1. 学校{{ technologyDetails.security_certified_count || 0 }}类平台通过国家安保等级认定。</p>
                <p>2. 学校部署的各类平台通过国家安保等级认定的比例为{{ getSecurityRatioText() }}。</p>
              </div>
            </div>
            <div class="info-item">
              <span class="info-label">数据风险事件记录</span>
              <div class="info-value">
                <p>近5年，学校{{ technologyDetails.has_security_incident ? '发生过' : '未发生' }}数据风险事件。</p>
              </div>
            </div>
          </div>
        </div>

        <!-- AI评估建议 -->
        <div class="ai-suggestion">
          <h4>评估建议：</h4>
          <p>{{ reportData.suggestions?.technology || '暂无建议' }}</p>
        </div>
      </section>

      <!-- 报告结尾 -->
      <div class="report-footer">
        <p>— 报告结束 —</p>
        <p class="footer-note">本报告由中小学校数据文化成熟度评估监测系统自动生成</p>
      </div>
    </div>
    <div v-else class="loading-container">
  <el-empty description="暂无报告数据，可能是由于评估尚未完成或计算未结束" />
  <el-button @click="goBack">返回上一页</el-button>
</div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getReportDataDetail  } from '@/api/assessment'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import html2canvas from 'html2canvas'
import { jsPDF }from 'jspdf'
import { ArrowLeft, Download, Loading, DataAnalysis, Reading, Document, TrendCharts, Files, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 状态
const loading = ref(true)
const downloading = ref(false)
const reportData = ref({})
const reportContainer = ref(null)
const reportContent = ref(null)

// 图表引用
const overviewChart = ref(null)
const teacherRadarChart = ref(null)
const managerRadarChart = ref(null)
const studentRadarChart = ref(null)
const literacyComparisonChart = ref(null)
const behaviorBarChart = ref(null)
const teacherEffectRadar = ref(null)
const studentEffectRadar = ref(null)
const assetAwarenessRadar = ref(null)

// 图表实例
let chartInstances = []

// 计算属性
const dimensionScores = computed(() => reportData.value.dimension_scores || {})
const secondaryScores = computed(() => reportData.value.secondary_scores || {})
const observationScores = computed(() => reportData.value.observation_scores || {})
const institutionDetails = computed(() => reportData.value?.institution || {})
const behaviorDetails = computed(() => reportData.value?.behavior || {})
const assetDetails = computed(() => reportData.value?.asset || {})
const technologyDetails = computed(() => reportData.value?.technology || {})

const dimensionList = computed(() => [
  { name: '数据素养', score: dimensionScores.value.literacy },
  { name: '数据制度', score: dimensionScores.value.institution },
  { name: '数据行为', score: dimensionScores.value.behavior },
  { name: '数据资产', score: dimensionScores.value.asset },
  { name: '数据技术', score: dimensionScores.value.technology }
])

// 生命周期
onMounted(async () => {
  const assessmentId = route.params.id
  if (!assessmentId) {
    ElMessage.error('缺少评估ID')
    router.back()
    return
  }
  await loadReportData(assessmentId)
})

onUnmounted(() => {
  // 销毁所有图表实例
  chartInstances.forEach(chart => chart?.dispose())
})

// 方法
const toNum = (v, def = 0) => {
  const n = parseFloat(v)
  return Number.isFinite(n) ? n : def
}

const loadReportData = async (assessmentId) => {
  loading.value = true
  try {
    const res = await getReportDataDetail(assessmentId)
    const raw = res || {} // res 本身就是你发的那个完整对象

    // 辅助工具：确保转为数字，防止后端传字符串导致图表崩溃
    const toF = (v) => parseFloat(v || 0)

    // 
    const processedData = {
      // 1. 基础信息
      school_name: raw.school_name || "学校名称",
      report_date: raw.report_date,
      maturity_level: raw.maturity_level || "未知",
      
      // 2. 总分（保持5分制）
      total_score:视觉处理(toF(raw.total_score || raw.scores?.total_score)),
      total_score_percent: toF(raw.total_score || raw.scores?.total_score), // 模板里可能叫这个名

      // 3. 五大维度得分对象（直接提取根部的 score 字段）
      dimension_scores: {
        literacy: toF(raw.dimension_scores.literacy),
        institution: toF(raw.dimension_scores.institution),
        behavior: toF(raw.dimension_scores.behavior),
        asset: toF(raw.dimension_scores.asset),
        technology: toF(raw.dimension_scores.technology)
      },

      // 4. 二级指标得分（如果后端没给，先用大维度分填充，保证页面文字描述有数据）
      secondary_scores: raw.secondary_scores || {
        A1: toF(raw.literacy_score), A2: toF(raw.literacy_score), A3: toF(raw.literacy_score),
        B1: toF(raw.institution_score), B2: toF(raw.institution_score), B3: toF(raw.institution_score),
        C1: toF(raw.behavior_score), C2: toF(raw.behavior_score),
        D1: toF(raw.asset_score), D2: toF(raw.asset_score),
        E1: toF(raw.technology_score), E2: toF(raw.technology_score)
      },

      // 5. 详情子集（直接引用原对象，方便文字描述读取）
      institution: raw.institution_details || {},
      behavior: raw.behavior_details || {},
      asset: raw.asset_details || {},
      technology: raw.technology_details || {},

      // 6. 补全缺失的雷达图观测点分
      observation_scores: raw.observation_scores || {},

      // 7. 补全AI建议
      suggestions: raw.suggestions || {
        overall: "AI诊断建议正在生成中...",
        literacy: "...", institution: "...", behavior: "...", asset: "...", technology: "..."
      },

      // 8. 补全参评人数
      participant_counts: raw.participant_counts || { teacher: 0, student: 0, manager: 0 },

      // 9. 平均分（5分制下默认 3.0）
      average_scores: raw.average_scores || {
        literacy: 3.0, institution: 3.0, behavior: 3.0, asset: 3.0, technology: 3.0
      }
    }

    // ✅ 最终赋值给响应式变量
    reportData.value = processedData

    // 只有数据装载完毕才初始化图表
    nextTick(() => {
      initAllCharts()
    })
  } catch (error) {
    console.error('数据加工失败:', error)
    ElMessage.error('报告数据加载异常')
  } finally {
    loading.value = false
  }
}

// 内部数值格式化辅助
function 视觉处理(num) {
  return parseFloat(num.toFixed(2))
}


const initAllCharts = () => {
  console.log('开始初始化图表...')
  // 确保先销毁旧实例
  chartInstances.forEach(chart => chart?.dispose())
  chartInstances = []
  
  setTimeout(() => {
    initOverviewChart()
    initLiteracyRadarCharts()
    initLiteracyComparisonChart()
    initBehaviorBarChart()
    initBehaviorRadarCharts()
    initAssetAwarenessRadar()
    console.log('图表初始化完成')
  }, 100)
}

// 概况柱状图
const initOverviewChart = () => {
  if (!overviewChart.value) {
    console.warn('找不到概况图表容器')
    return
  }
  try {
    const chart = echarts.init(overviewChart.value)
    chartInstances.push(chart)

    const dimensions = ['数据素养', '数据制度', '数据行为', '数据资产', '数据技术']
  const scores = [
      (dimensionScores.value.literacy || 0).toFixed(1),
      (dimensionScores.value.institution || 0).toFixed(1),
      (dimensionScores.value.behavior || 0).toFixed(1),
      (dimensionScores.value.asset || 0).toFixed(1),
      (dimensionScores.value.technology || 0).toFixed(1)
    ]
    // 从后端获取平均分，如果没有则使用默认值60
    const avgScoresData = reportData.value.average_scores || {}
    const avgScores = [
      (avgScoresData.literacy ?? 3.0).toFixed(1),
      (avgScoresData.institution ?? 3.0).toFixed(1),
      (avgScoresData.behavior ?? 3.0).toFixed(1),
      (avgScoresData.asset ?? 3.0).toFixed(1),
      (avgScoresData.technology ?? 3.0).toFixed(1),
    ]

    chart.setOption({
      title: { text: '五维度得分对比', left: 'center', top: 10 },
      tooltip: { trigger: 'axis' },
      legend: { data: ['真实得分', '平均得分'], top: 40 },
      grid: { left: '3%', right: '4%', bottom: '3%', top: 80, containLabel: true },
      xAxis: { type: 'category', data: dimensions },
      yAxis: { type: 'value', max: 5 },
      series: [
        {
          name: '真实得分',
          type: 'bar',
          data: scores,
          itemStyle: { color: '#409eff' },
          label: { 
            show: true, 
            position: 'top',
            formatter: (params) => params.value
          }
        },
        {
          name: '平均得分',
          type: 'bar',
          data: avgScores,
          itemStyle: { color: '#e6a23c' },
          label: { 
            show: true, 
            position: 'top',
            formatter: (params) => params.value
          }
        }
      ]
    })
  } catch (e) {
    console.error('概况图表初始化失败:', e)
  }
}

// 数据素养雷达图
const initLiteracyRadarCharts = () => {
  const indicators = [
    { name: '数据意识与思维', max: 5 },
    { name: '数据知识与技能', max: 5 },
    { name: '数据评价与交流', max: 5 },
    { name: '数据应用与创新', max: 5 },
    { name: '数据伦理与隐私', max: 5 }
  ]

  // 教师雷达图
  if (teacherRadarChart.value) {
    try {
      const chart = echarts.init(teacherRadarChart.value)
      chartInstances.push(chart)
      chart.setOption({
        title: { text: '教师数据素养', left: 'center', top: 5, textStyle: { fontSize: 14 } },
        radar: { 
          indicator: indicators, 
          radius: '60%', 
          center: ['50%', '55%'],
          axisName: { color: '#666', fontSize: 10 }
        },
        series: [{
          type: 'radar',
          data: [{
            value: [
              observationScores.value['A11'] || 0,
              observationScores.value['A12'] || 0,
              observationScores.value['A13'] || 0,
              observationScores.value['A14'] || 0,
              observationScores.value['A15'] || 0
            ],
            name: '教师',
            areaStyle: { color: 'rgba(64, 158, 255, 0.3)' }
          }],
          itemStyle: { color: '#409eff' }
        }]
      })
    } catch (e) {
      console.error('教师雷达图初始化失败:', e)
    }
  }

  // 管理者雷达图
  if (managerRadarChart.value) {
    try {
      const chart = echarts.init(managerRadarChart.value)
      chartInstances.push(chart)
      chart.setOption({
        title: { text: '管理者数据素养', left: 'center', top: 5, textStyle: { fontSize: 14 } },
        radar: { 
          indicator: indicators, 
          radius: '60%', 
          center: ['50%', '55%'],
          axisName: { color: '#666', fontSize: 10 }
        },
        series: [{
          type: 'radar',
          data: [{
            value: [
              observationScores.value['A21'] || 0,
              observationScores.value['A22'] || 0,
              observationScores.value['A23'] || 0,
              observationScores.value['A24'] || 0,
              observationScores.value['A25'] || 0
            ],
            name: '管理者',
            areaStyle: { color: 'rgba(103, 194, 58, 0.3)' }
          }],
          itemStyle: { color: '#67c23a' }
        }]
      })
    } catch (e) {
      console.error('管理者雷达图初始化失败:', e)
    }
  }

  // 学生雷达图
  if (studentRadarChart.value) {
    try {
      const chart = echarts.init(studentRadarChart.value)
      chartInstances.push(chart)
      chart.setOption({
        title: { text: '学生数据素养', left: 'center', top: 5, textStyle: { fontSize: 14 } },
        radar: { 
          indicator: indicators, 
          radius: '60%', 
          center: ['50%', '55%'],
          axisName: { color: '#666', fontSize: 10 }
        },
        series: [{
          type: 'radar',
          data: [{
            value: [
              observationScores.value['A31'] || 0,
              observationScores.value['A32'] || 0,
              observationScores.value['A33'] || 0,
              observationScores.value['A34'] || 0,
              observationScores.value['A35'] || 0
            ],
            name: '学生',
            areaStyle: { color: 'rgba(144, 147, 153, 0.3)' }
          }],
          itemStyle: { color: '#909399' }
        }]
      })
    } catch (e) {
      console.error('学生雷达图初始化失败:', e)
    }
  }
}

// 数据素养综合对比柱状图
const initLiteracyComparisonChart = () => {
  if (!literacyComparisonChart.value) return
  try {
    const chart = echarts.init(literacyComparisonChart.value)
    chartInstances.push(chart)

    const categories = ['数据意识与思维', '数据知识与技能', '数据评价与交流', '数据应用与创新', '数据伦理与隐私']

    chart.setOption({
      title: { text: '教师、管理者、学生数据素养对比', left: 'center', top: 10 },
      tooltip: { 
        trigger: 'axis',
        valueFormatter: (value) => value ? value.toFixed(2) : '0.00'
      },
      legend: { data: ['教师', '管理者', '学生'], top: 40 },
      grid: { left: '3%', right: '4%', bottom: '3%', top: 80, containLabel: true },
      xAxis: { type: 'category', data: categories },
      yAxis: { type: 'value', max: 5, name: '分数(分)' },
      series: [
        {
          name: '教师',
          type: 'bar',
          data: [
            observationScores.value['A11'] || 0,
            observationScores.value['A12'] || 0,
            observationScores.value['A13'] || 0,
            observationScores.value['A14'] || 0,
            observationScores.value['A15'] || 0
          ],
          itemStyle: { color: '#409eff' }
        },
        {
          name: '管理者',
          type: 'bar',
          data: [
            observationScores.value['A21'] || 0,
            observationScores.value['A22'] || 0,
            observationScores.value['A23'] || 0,
            observationScores.value['A24'] || 0,
            observationScores.value['A25'] || 0
          ],
          itemStyle: { color: '#67c23a' }
        },
        {
          name: '学生',
          type: 'bar',
          data: [
            observationScores.value['A31'] || 0,
            observationScores.value['A32'] || 0,
            observationScores.value['A33'] || 0,
            observationScores.value['A34'] || 0,
            observationScores.value['A35'] || 0
          ],
          itemStyle: { color: '#909399' }
        }
      ]
    })
  } catch (e) {
    console.error('数据素养对比图初始化失败:', e)
  }
}

// 数据行为横向柱状图
const initBehaviorBarChart = () => {
  if (!behaviorBarChart.value) return
  try {
    const chart = echarts.init(behaviorBarChart.value)
    chartInstances.push(chart)

    chart.setOption({
      title: { text: '月度数据行为频次统计', left: 'center', top: 5 },
      tooltip: { trigger: 'axis' },
      grid: { left: '15%', right: '10%', bottom: '10%', top: 50 },
      xAxis: { type: 'value', name: '月均频次(次)' },
      yAxis: {
        type: 'category',
        data: ['管理者数据行为', '学生数据行为', '教师数据行为']
      },
      series: [{
        type: 'bar',
        data: [
          { value: behaviorDetails.value.manager_login_freq || 0, itemStyle: { color: '#67c23a' } },
          { value: behaviorDetails.value.student_login_freq || 0, itemStyle: { color: '#e6a23c' } },
          { value: behaviorDetails.value.teacher_login_freq || 0, itemStyle: { color: '#409eff' } }
        ],
        label: { show: true, position: 'right' }
      }]
    })
  } catch (e) {
    console.error('数据行为柱状图初始化失败:', e)
  }
}

// 数据行为效果雷达图
const initBehaviorRadarCharts = () => {
  const indicators = [
    { name: '数据意识与思维', max: 5 },
    { name: '数据知识与技能', max: 5 },
    { name: '数据评价与交流', max: 5 },
    { name: '数据应用与创新', max: 5 },
    { name: '数据伦理与隐私', max: 5 }
  ]

  if (teacherEffectRadar.value) {
    try {
      const chart = echarts.init(teacherEffectRadar.value)
      chartInstances.push(chart)
      chart.setOption({
        title: { text: '教师数据素养', left: 'center', top: 5, textStyle: { fontSize: 13 } },
        radar: { 
          indicator: indicators, 
          radius: '55%', 
          center: ['50%', '55%'],
          axisName: { color: '#666', fontSize: 10 }
        },
        series: [{
          type: 'radar',
          data: [{
            value: [
              observationScores.value['A11'] || 0,
              observationScores.value['A12'] || 0,
              observationScores.value['A13'] || 0,
              observationScores.value['A14'] || 0,
              observationScores.value['A15'] || 0
            ],
            name: '教师数据素养',
            areaStyle: { color: 'rgba(64, 158, 255, 0.3)' }
          }],
          itemStyle: { color: '#409eff' }
        }]
      })
    } catch (e) {
      console.error('教师行为雷达图初始化失败:', e)
    }
  }

  if (studentEffectRadar.value) {
    try {
      const chart = echarts.init(studentEffectRadar.value)
      chartInstances.push(chart)
      chart.setOption({
        title: { text: '学生数据素养', left: 'center', top: 5, textStyle: { fontSize: 13 } },
        radar: { 
          indicator: indicators, 
          radius: '55%', 
          center: ['50%', '55%'],
          axisName: { color: '#666', fontSize: 10 }
        },
        series: [{
          type: 'radar',
          data: [{
            value: [
              observationScores.value['A31'] || 0,
              observationScores.value['A32'] || 0,
              observationScores.value['A33'] || 0,
              observationScores.value['A34'] || 0,
              observationScores.value['A35'] || 0
            ],
            name: '学生数据素养',
            areaStyle: { color: 'rgba(144, 147, 153, 0.3)' }
          }],
          itemStyle: { color: '#909399' }
        }]
      })
    } catch (e) {
      console.error('学生行为雷达图初始化失败:', e)
    }
  }
}

// 数据资产意识雷达图
const initAssetAwarenessRadar = () => {
  if (!assetAwarenessRadar.value) return
  try {
    const chart = echarts.init(assetAwarenessRadar.value)
    chartInstances.push(chart)

    chart.setOption({
      title: { text: '数据资产意识雷达图', left: 'center', top: 10 },
      radar: {
        indicator: [
          { name: '数据资产价值意识', max: 5 },
          { name: '数据资产应用意识', max: 5 },
          { name: '数据资产治理意识', max: 5 }
        ],
        radius: '60%',
        center: ['50%', '55%'],
        axisName: { color: '#666', fontSize: 10 }
      },
      series: [{
        type: 'radar',
        data: [{
          value: [
            observationScores.value['D11'] || 0,
            observationScores.value['D12'] || 0,
            observationScores.value['D13'] || 0
          ],
          name: '资产意识',
          areaStyle: { color: 'rgba(64, 158, 255, 0.3)' }
        }],
        itemStyle: { color: '#409eff' }
      }]
    })
  } catch (e) {
    console.error('资产雷达图初始化失败:', e)
  }
}

// 辅助方法
const formatDate = (dateStr) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

const getPerformanceText = (score) => {
  if (score >= 4.5) return '表现优秀'
  if (score >= 3.5) return '表现均衡'
  return '有待提升'
}

const getLevelNumber = (level) => {
  const map = { '初始级': '第1级', '成长级': '第2级', '成熟级': '第3级', '引领级': '第4级' }
  return map[level] || ''
}

const getTotalManagementDocs = () => {
  const d = institutionDetails.value
  return d.management_doc_count || 0
}

const getTotalPracticeDocs = () => {
  const d = institutionDetails.value
  return d.practice_doc_count || 0
}

const getTotalCases = () => {
  const d = behaviorDetails.value
  return (d.case_national_count || 0) + (d.case_provincial_count || 0) + (d.case_city_count || 0)
}

const getTotalAwards = () => {
  const d = behaviorDetails.value
  return (d.award_national_count || 0) + (d.award_provincial_count || 0) + (d.award_city_count || 0)
}

const getTotalMedia = () => {
  const d = behaviorDetails.value
  return (d.media_national_count || 0) + (d.media_provincial_count || 0) + (d.media_city_count || 0)
}

const getTotalConference = () => {
  const d = behaviorDetails.value
  return (d.conference_national_count || 0) + (d.conference_provincial_count || 0) + (d.conference_city_count || 0)
}

const formatDataVolume = (volume) => {
  if (!volume) return '0 GB'
  return `${volume.toFixed(0)} GB`
}

const getPerCapitaVolume = () => {
  const total = assetDetails.value.total_data_volume || 0
  const people = (assetDetails.value.student_count || 0) + (assetDetails.value.staff_count || 0)
  if (people === 0) return '0'
  return (total / people).toFixed(1)
}

const getVolumePercentage = (value, max) => {
  if (!value || !max) return 0
  return Math.min(100, (value / max) * 100)
}

const getDataCenterText = () => {
  const standard = technologyDetails.value.data_center_standard
  if (standard === 'fully_compliant') return '建有独立数据中心且指标完全达到B级要求'
  if (standard === 'partially_compliant') return '建有独立数据中心且指标部分达到B级要求'
  return '数据中心指标未达到B级要求'
}

const getSecurityRatioText = () => {
  const ratio = technologyDetails.value.security_certified_ratio
  if (ratio === 'high') return '80%以上'
  if (ratio === 'medium') return '40%-80%'
  return '40%以下'
}

const goBack = () => {
  router.back()
}

// PDF下载 - 单页完整显示，不分页
const downloadPDF = async () => {
  if (!reportContent.value) return
  
  downloading.value = true
  ElMessage.info('正在生成PDF，请稍候...')

  try {
    const element = reportContent.value
    
    // 整体截图
    const canvas = await html2canvas(element, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff',
      windowWidth: element.scrollWidth,
      height: element.scrollHeight,
      scrollY: -window.scrollY
    })

    const imgData = canvas.toDataURL('image/png', 1.0)
    
    // A4宽度 210mm，根据内容高度动态计算PDF高度
    const pdfWidth = 210
    const imgWidth = canvas.width
    const imgHeight = canvas.height
    const ratio = pdfWidth / imgWidth
    const pdfHeight = imgHeight * ratio
    
    // 创建自定义尺寸的PDF（宽度A4，高度根据内容）
    const pdf = new jsPDF('p', 'mm', [pdfWidth, pdfHeight])
    
    pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight)

    pdf.save(`${reportData.value.school_name || '学校'}_数据文化成熟度评估报告.pdf`)
    ElMessage.success('PDF下载成功')
  } catch (error) {
    console.error('生成PDF失败:', error)
    ElMessage.error('生成PDF失败，请重试')
  } finally {
    downloading.value = false
  }
}
</script>

<style scoped>
.report-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.report-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #fff;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h1 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  color: #909399;
}

.loading-icon {
  font-size: 48px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.report-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px;
  background: #fff;
}

/* 报告标题 */
.report-title-section {
  text-align: center;
  padding: 40px 0;
  border-bottom: 2px solid #409eff;
  margin-bottom: 30px;
}

.main-title {
  font-size: 28px;
  color: #303133;
  margin: 0 0 16px 0;
}

.report-date {
  color: #909399;
  font-size: 14px;
}

/* 报告说明 */
.report-intro {
  background: #ecf5ff;
  padding: 24px;
  border-radius: 8px;
  margin-bottom: 40px;
  line-height: 1.8;
}

.report-intro p {
  margin: 0 0 16px 0;
  color: #606266;
}

.report-intro ol {
  margin: 0;
  padding-left: 20px;
}

.report-intro li {
  margin-bottom: 8px;
  color: #606266;
}

/* 章节样式 */
.report-section {
  margin-bottom: 50px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 22px;
  color: #303133;
  padding-bottom: 12px;
  border-bottom: 2px solid #409eff;
  margin-bottom: 20px;
}

.section-title .el-icon {
  color: #409eff;
}

.section-summary {
  color: #606266;
  line-height: 1.8;
  margin-bottom: 24px;
}

/* 概况得分卡片 */
.overview-scores {
  display: flex;
  gap: 24px;
  margin-bottom: 30px;
}

.score-card {
  flex: 1;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.score-card.total {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: #fff;
}

.score-card.level {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  color: #fff;
}

.score-card .label {
  display: block;
  font-size: 14px;
  margin-bottom: 8px;
  opacity: 0.9;
}

.score-card .value {
  font-size: 28px;
  font-weight: bold;
}

/* 概况图表区域 */
.overview-chart-container {
  display: flex;
  gap: 24px;
  margin-bottom: 30px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.overview-left {
  width: 200px;
  background: #f5f7fa;
  padding: 16px;
}

.dimension-list {
  background: #fff;
  border-radius: 6px;
  overflow: hidden;
}

.dimension-header {
  background: #409eff;
  color: #fff;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 400;
  font-size: 10px;
}

.total-score-badge {
  background: #e6a23c;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.level-badge {
  background: #67c23a;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.dimension-item {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
}

.dimension-item:last-child {
  border-bottom: none;
}

.dim-name {
  color: #606266;
}

.dim-score {
  color: #303133;
  font-weight: 500;
}

.overview-right {
  flex: 1;
  padding: 16px;
}

/* AI建议 */
.ai-suggestion {
  background: #fdf6ec;
  padding: 20px;
  border-radius: 8px;
  margin: 24px 0;
  border-left: 4px solid #e6a23c;
}

.ai-suggestion h4 {
  margin: 0 0 12px 0;
  color: #e6a23c;
}

.ai-suggestion p {
  margin: 0;
  color: #606266;
  line-height: 1.8;
}

.evaluation-note {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin-top: 20px;
}

.evaluation-note h4 {
  margin: 0 0 8px 0;
  color: #909399;
  font-size: 14px;
}

.evaluation-note p {
  margin: 0;
  color: #909399;
  font-size: 13px;
}

/* 数据素养得分卡片 */
.literacy-scores {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
}

.literacy-score-card {
  flex: 1;
  text-align: center;
  padding: 20px;
  border-radius: 8px;
}

.literacy-score-card.teacher {
  border-bottom: 4px solid #409eff;
  background: #f0f9ff;
}

.literacy-score-card.manager {
  border-bottom: 4px solid #67c23a;
  background: #f0f9eb;
}

.literacy-score-card.student {
  border-bottom: 4px solid #909399;
  background: #f5f7fa;
}

.literacy-score-card .score {
  display: block;
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
}

.literacy-score-card.teacher .score { color: #409eff; }
.literacy-score-card.manager .score { color: #67c23a; }
.literacy-score-card.student .score { color: #909399; }

.literacy-score-card .label {
  color: #606266;
  font-size: 14px;
}

.participant-info {
  display: flex;
  justify-content: center;
  gap: 40px;
  color: #606266;
  margin-bottom: 24px;
}

/* 雷达图区域 */
.literacy-radar-section,
.literacy-comparison-section {
  margin: 30px 0;
}

.literacy-radar-section h4,
.literacy-comparison-section h4 {
  color: #606266;
  margin-bottom: 16px;
}

.radar-charts-row {
  display: flex;
  gap: 16px;
}

.radar-chart-item {
  flex: 1;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 10px;
}

/* 制度卡片 */
.institution-card,
.behavior-card,
.asset-card,
.tech-card {
  background: #ecf5ff;
  border-radius: 8px;
  margin-bottom: 20px;
  overflow: hidden;
}

.card-header {
  background: #409eff;
  color: #fff;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-weight: 500;
}

.card-subtitle {
  font-size: 13px;
  opacity: 0.9;
}

.card-content {
  padding: 20px;
}

.info-item {
  margin-bottom: 16px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-label {
  display: block;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.info-value {
  color: #606266;
  line-height: 1.8;
}

.info-value p {
  margin: 4px 0;
}

/* 大模型分析结果样式 */
.llm-analysis {
  margin-top: 8px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.llm-analysis p {
  color: #409eff;
  font-weight: 500;
  margin-bottom: 8px;
}

.analysis-content {
  color: #606266;
  font-size: 13px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 计分规则说明 */
.scoring-rules {
  background-color: #f0f9eb;
  border-left: 5px solid #67c23a;
  padding: 16px;
  margin-bottom: 24px;
  border-radius: 4px;
}

.scoring-rules h4 {
  color: #67c23a;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
}

.scoring-rules p {
  color: #606266;
  margin: 0 0 8px 0;
  font-size: 14px;
  line-height: 1.6;
}

.scoring-rules ul {
  margin: 8px 0 12px 20px;
  padding: 0;
  color: #606266;
  font-size: 14px;
}

.scoring-rules li {
  margin-bottom: 6px;
  line-height: 1.6;
}

.scoring-rules .rule-note {
  font-size: 12px;
  color: #909399;
  font-style: italic;
  margin-top: 8px;
}

/* 行为统计 */
.login-stats {
  margin-bottom: 16px;
}

.login-stats p {
  margin: 8px 0;
  color: #606266;
}

.achievement-section {
  margin-bottom: 20px;
}

.achievement-section h5 {
  color: #409eff;
  margin: 0 0 8px 0;
}

.achievement-section p {
  margin: 0;
  color: #606266;
}

.behavior-radar-row {
  display: flex;
  gap: 16px;
  margin-top: 16px;
}

/* 资产进度条 */
.staff-info {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 24px;
  color: #606266;
}

.asset-progress-section {
  display: flex;
  gap: 24px;
}

.progress-card {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.progress-header {
  margin-bottom: 12px;
}

.progress-title {
  color: #909399;
  font-size: 13px;
}

.progress-value {
  font-size: 28px;
  font-weight: bold;
  color: #67c23a;
  margin-bottom: 8px;
}

.progress-value.red {
  color: #f56c6c;
}

.progress-label {
  color: #909399;
  font-size: 12px;
  margin-bottom: 12px;
}

.progress-range {
  display: flex;
  justify-content: space-between;
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}

/* 报告结尾 */
.report-footer {
  text-align: center;
  padding: 40px 0;
  color: #909399;
  border-top: 1px solid #e4e7ed;
  margin-top: 40px;
}

.footer-note {
  font-size: 12px;
  margin-top: 8px;
}

/* 图表容器 */
.chart-box {
  width: 100%;
}

/* 分页符（PDF打印用） */
.page-break {
  page-break-before: always;
}

/* 打印时隐藏操作栏 */
@media print {
  .no-print {
    display: none !important;
  }
  
  .report-content {
    padding: 0;
  }
}
</style>
