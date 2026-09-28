<?xml version="1.0" encoding="UTF-8"?>

<!-- ================================================================= -->
<!-- Custom HTML stylesheet for the Student Workbook web targets.      -->
<!--                                                                   -->
<!-- Imports the standard PreTeXt HTML conversion and folds a          -->
<!-- chapter's <introduction> back onto the chapter's summary page.    -->
<!--                                                                   -->
<!-- Stock HTML gives a summary division's introduction its own web    -->
<!-- page (the "division companion chunk" opt-in). The SW chapter      -->
<!-- introductions hold only an opener image, so that lone page looks  -->
<!-- empty. The Teaching Guides read fine either way, so this override -->
<!-- is wired into the *-sw-web targets only, via each target's        -->
<!-- xsl="custom-html-sw.xsl" attribute in project.ptx.                -->
<!--                                                                   -->
<!-- The import href "./core/pretext-html.xsl" is the path the CLI     -->
<!-- sets up at build time (core copied into a "core" subdirectory),   -->
<!-- the same arrangement xsl/custom-latex.xsl uses for print.         -->
<!-- ================================================================= -->

<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    version="1.0">

    <xsl:import href="./core/pretext-html.xsl"/>

    <!-- =============================================================== -->
    <!-- Turn off the division-companion page opt-in                     -->
    <!--                                                                 -->
    <!-- pretext-common.xsl defaults this to false(); pretext-html.xsl   -->
    <!-- overrides it to true(), which is what makes a summary chapter's -->
    <!-- introduction a page of its own. Restating the common default    -->
    <!-- stops that: the introduction becomes inline content of its      -->
    <!-- parent's page, and gets no separate page and no nav link. On    -->
    <!-- its own this would DROP the introduction, because the stock     -->
    <!-- summary page (mode="intermediate") renders only the nav links,  -->
    <!-- never the companion body. The template override below puts the  -->
    <!-- introduction back, inline, so nothing is lost.                  -->
    <!-- =============================================================== -->
    <xsl:variable name="b-division-companion-chunks" select="false()"/>

    <!-- =============================================================== -->
    <!-- Chapter summary page, with the introduction folded in           -->
    <!--                                                                 -->
    <!-- A copy of stock's  match="&STRUCTURAL;" mode="intermediate"     -->
    <!-- (pretext-html.xsl), narrowed to  match="chapter"  so it wins    -->
    <!-- for chapters only and leaves book/frontmatter summary pages to  -->
    <!-- stock. The one addition is the <introduction> apply-templates   -->
    <!-- before the nav, which renders the chapter opener inline (via    -->
    <!-- the stock inline introduction template) instead of on a page    -->
    <!-- of its own. The frontmatter-without-titlepage special case in   -->
    <!-- the stock template is dropped: a chapter is never frontmatter.  -->
    <!--                                                                 -->
    <!-- Coupled to that stock template; re-check on a CLI upgrade —     -->
    <!-- see DOCUMENTATION/reference/version-baseline.md.                -->
    <!-- =============================================================== -->
    <xsl:template match="chapter" mode="intermediate">
        <xsl:apply-templates select="." mode="file-wrap">
            <xsl:with-param name="content">
                <!-- location info for debugging efforts -->
                <xsl:apply-templates select="." mode="debug-location" />
                <!-- Heading, div for this structural subdivision -->
                <section class="{local-name(.)}">
                    <xsl:apply-templates select="." mode="html-id-attribute"/>
                    <xsl:apply-templates select="." mode="section-heading">
                        <xsl:with-param name="heading-level" select="$chunk-heading-level"/>
                    </xsl:apply-templates>
                    <xsl:apply-templates select="." mode="author-byline"/>
                    <xsl:apply-templates select="titlepage|abstract">
                        <xsl:with-param name="heading-level" select="$chunk-heading-level + 1"/>
                    </xsl:apply-templates>
                    <!-- Fold the chapter introduction onto this summary   -->
                    <!-- page (stock would give it a page of its own).     -->
                    <xsl:apply-templates select="introduction">
                        <xsl:with-param name="heading-level" select="$chunk-heading-level + 1"/>
                    </xsl:apply-templates>
                    <!-- Links to subsidiary divisions, as a group of button/hyperlinks -->
                    <nav class="summary-links">
                        <ul>
                            <xsl:apply-templates select="*" mode="summary-nav" />
                        </ul>
                    </nav>
                    <!-- Insert permalink -->
                    <xsl:apply-templates select="." mode="permalink"/>
                </section>
            </xsl:with-param>
        </xsl:apply-templates>
    </xsl:template>

</xsl:stylesheet>
