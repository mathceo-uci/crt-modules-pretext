<?xml version="1.0" encoding="UTF-8"?>

<!-- ================================================================= -->
<!-- Custom LaTeX stylesheet for the CRT curriculum print targets.     -->
<!--                                                                   -->
<!-- Imports the standard PreTeXt LaTeX conversion and layers project- -->
<!-- specific overrides on top. Wired into the *-print targets in      -->
<!-- project.ptx via each target's  xsl="custom-latex.xsl"  attribute. -->
<!--                                                                   -->
<!-- The import href "./core/pretext-latex.xsl" is the path the CLI    -->
<!-- sets up at build time: it copies this xsl/ directory plus the     -->
<!-- core stylesheets into a temp dir, with core placed in a "core"    -->
<!-- subdirectory (see pretext.utils.copy_custom_xsl).                 -->
<!-- ================================================================= -->

<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    version="1.0">

    <xsl:import href="./core/pretext-latex.xsl"/>

    <!-- =============================================================== -->
    <!-- Workspace on a task, shown as a visible box                     -->
    <!--                                                                 -->
    <!-- A workspace="..." asks for blank space for students to write    -->
    <!-- in. PreTeXt leaves that space empty, with nothing drawn around  -->
    <!-- it. We want a visible box instead. This code draws one.         -->
    <!--                                                                 -->
    <!-- PreTeXt fills the space with an invisible strut, the line       -->
    <!-- \rule{\ptxworkspacestrutwidth}{height}, whose width is 0pt      -->
    <!-- except in draft mode. The template below is stock PreTeXt       -->
    <!-- copied unchanged, with that one line swapped for our own        -->
    <!-- \workspacebox{height}, which draws the green write in box.      -->
    <!-- The macro is defined in customPreambleLate.tex.                 -->
    <!--                                                                 -->
    <!-- This affects a workspace on a task, and the inline and project  -->
    <!-- cases, which are the ones PreTeXt sends through the template    -->
    <!-- named "workspace". A workspace on an exercise does NOT come     -->
    <!-- through here. PreTeXt passes its height to the divisionexercise -->
    <!-- box as an argument, and the box draws it. That path is dealt    -->
    <!-- with in customPreambleLate.tex, where the box is redefined to   -->
    <!-- call \workspacebox as well, so both kinds of workspace end up   -->
    <!-- looking the same.                                               -->
    <!-- =============================================================== -->
    <xsl:template match="*" mode="workspace">
        <xsl:variable name="vertical-space">
            <xsl:apply-templates select="." mode="sanitize-workspace"/>
        </xsl:variable>
        <xsl:if test="not($vertical-space = '')">
            <xsl:text>\par\workspacebox{</xsl:text>
            <xsl:value-of select="$vertical-space"/>
            <xsl:text>}%&#xa;</xsl:text>
        </xsl:if>
    </xsl:template>

    <!-- =============================================================== -->
    <!-- A tabular in a side-by-side panel: no \resizebox                -->
    <!--                                                                 -->
    <!-- PreTeXt wraps such a table in \resizebox and shrinks it when it -->
    <!-- is too wide for its panel. The table then prints at a different -->
    <!-- size from the text around it. This code removes the wrapper.    -->
    <!--                                                                 -->
    <!-- The table also comes out centred now. PreTeXt already asks for  -->
    <!-- that, but the request did nothing inside the box \resizebox     -->
    <!-- builds, so the table sat against the left edge of its panel.    -->
    <!--                                                                 -->
    <!-- A table too wide for its panel now runs over the edge, where it -->
    <!-- can be seen and fixed. Widen the panel, or give the wide column -->
    <!-- a col/@width and a <p> in each of its body cells so it wraps.   -->
    <!-- =============================================================== -->
    <xsl:template match="tabular[ancestor::sidebyside]">
        <xsl:apply-templates select="." mode="tabular-inclusion"/>
    </xsl:template>

    <!-- =============================================================== -->
    <!-- A latex-image: no \resizebox, so it prints at native size       -->
    <!--                                                                 -->
    <!-- PreTeXt wraps every latex-image in \resizebox{\linewidth}{!},   -->
    <!-- which stretches the whole picture to fill the column, whatever  -->
    <!-- size the picture was drawn. That distorts everything absolute   -->
    <!-- in it. A pgfplots graph sizes itself from inside with its       -->
    <!-- width=/height= keys and sets line widths, mark sizes and fonts  -->
    <!-- in real points; a hand-drawn TikZ box is laid out in cm. The    -->
    <!-- \resizebox rescales all of that by whatever factor fills the    -->
    <!-- column, so none of it prints at the size it was given. This     -->
    <!-- code drops the \resizebox and centres the picture instead, so   -->
    <!-- it prints at the size it was authored in.                       -->
    <!--                                                                 -->
    <!-- Sizing now lives entirely in the image code (a pgfplots axis,   -->
    <!-- or the cm coordinates of a TikZ box), not in the image's        -->
    <!-- @width/@margins, which no longer scale it. A picture wider than -->
    <!-- the text block overflows the margin rather than shrinking, the  -->
    <!-- same choice the sidebyside-tabular override above makes: native -->
    <!-- size, and visible when it is too big so it can be fixed at the  -->
    <!-- source.                                                         -->
    <!-- =============================================================== -->
    <xsl:template match="image[latex-image]" mode="image-inclusion">
        <xsl:text>\begin{center}%&#xa;</xsl:text>
        <xsl:apply-templates select="latex-image"/>
        <xsl:text>\end{center}%&#xa;</xsl:text>
    </xsl:template>

    <!-- =============================================================== -->
    <!-- Extra \documentclass options                                    -->
    <!--                                                                 -->
    <!-- PreTeXt has no way to add extra \documentclass options besides  -->
    <!-- the ones it supports. This code inserts more options.           -->
    <!--                                                                 -->
    <!-- It works by overriding "sidedness", the stock template whose    -->
    <!-- only job is to print the word oneside or twoside. PreTeXt       -->
    <!-- calls that template in four places, and all four are a          -->
    <!-- \documentclass[...] line, so anything we print after it can     -->
    <!-- only land there. The xsl:choose below is stock PreTeXt, copied  -->
    <!-- unchanged. The xsl:text after it is what we are adding.         -->
    <!--                                                                 -->
    <!-- Two options are added:                                          -->
    <!--                                                                 -->
    <!-- openany (currently on)                                          -->
    <!--   A chapter starts on the next page, whether that page is a     -->
    <!--   left or a right one. Without it the book class starts every   -->
    <!--   chapter on a right-hand page, inserting a blank page when it  -->
    <!--   has to. The publication file's open-odd attribute cannot do   -->
    <!--   this. All it can do is force chapters onto odd pages when     -->
    <!--   printing one-sided.                                           -->
    <!--                                                                 -->
    <!-- landscape (currently off)                                       -->
    <!--   Turns the paper sideways. It has to be set here and not in    -->
    <!--   the geometry package. Set here, the paper itself changes      -->
    <!--   size, and the PDF page changes with it. Set in geometry,      -->
    <!--   only the block of text turns sideways while the page stays    -->
    <!--   portrait, so the text runs off the page.                      -->
    <!--                                                                 -->
    <!--   If you turn it back on, check customPreambleLate.tex. Its     -->
    <!--   \geometry calls must not say landscape too, or the paper      -->
    <!--   turns twice and ends up portrait again. Its margins are also  -->
    <!--   chosen to suit the paper, so they need new values. Both are   -->
    <!--   explained in the PAGE GEOMETRY block of that file.            -->
    <!-- =============================================================== -->
    <xsl:template name="sidedness">
        <xsl:choose>
            <xsl:when test="$latex-sides = 'one'">
                <xsl:text>oneside</xsl:text>
            </xsl:when>
            <xsl:when test="$latex-sides = 'two'">
                <xsl:text>twoside</xsl:text>
            </xsl:when>
        </xsl:choose>
        <xsl:text>,openany</xsl:text>
        <!-- <xsl:text>,landscape</xsl:text> -->
    </xsl:template>

    <!-- =============================================================== -->
    <!-- A tabular with @rowstretch: taller rows, in LaTeX output only   -->
    <!--                                                                 -->
    <!-- PreTeXt has no setting for the height of table rows, and an     -->
    <!-- \arraystretch set in the preamble stretches every tabular in    -->
    <!-- the book. A worksheet table that students write into needs      -->
    <!-- rows taller than their text, and only that table should get     -->
    <!-- them. This code catches any tabular that has @rowstretch and    -->
    <!-- wraps PreTeXt's normal output for it in a group that sets       -->
    <!-- \arraystretch to that value, so only this table is stretched;  -->
    <!-- \endgroup puts the default back for everything after it. The    -->
    <!-- table itself still comes from the stock templates, via         -->
    <!-- apply-imports, so its borders and alignment are unchanged.      -->
    <!--                                                                 -->
    <!-- Usage: <tabular rowstretch="1.5">. The value multiplies the     -->
    <!-- normal row height, so 1.5 gives rows half again as tall.       -->
    <!--                                                                 -->
    <!-- Only the LaTeX output changes; HTML ignores @rowstretch, and    -->
    <!-- rows there keep their usual height. The attribute is not in     -->
    <!-- the PreTeXt schema, so validation flags it; the build does      -->
    <!-- not care. A tabular inside a sidebyside goes through other      -->
    <!-- templates (see the sidebyside-tabular override above) and may  -->
    <!-- not be caught here.                                            -->
    <!-- =============================================================== -->
    <xsl:template match="tabular[@rowstretch]">
      <xsl:text>\begingroup\renewcommand{\arraystretch}{</xsl:text>
      <xsl:value-of select="@rowstretch"/>
      <xsl:text>}%&#xa;</xsl:text>
      <xsl:apply-imports/>
      <xsl:text>\endgroup%&#xa;</xsl:text>
    </xsl:template>

    <!-- =============================================================== -->
    <!-- The monospace font, loaded in every book                        -->
    <!--                                                                 -->
    <!-- PreTeXt loads its monospace font, Inconsolata, only when a book -->
    <!-- contains an element such as <c>, <pre> or <program>. A <url>    -->
    <!-- does not count, even though print sets its address in           -->
    <!-- monospace after the link text. A book with no such element      -->
    <!-- falls back to Latin Modern Mono, which is wider, so the same    -->
    <!-- address took more room and broke across two lines in Hawaii     -->
    <!-- and not in the other workbooks. (Those only got Inconsolata     -->
    <!-- from a <c> inside a TODO, which never prints.)                  -->
    <!--                                                                 -->
    <!-- This line says every book needs the monospace font, which is    -->
    <!-- true because every book prints web addresses. PreTeXt then      -->
    <!-- loads Inconsolata in the usual way, so the choice of font stays -->
    <!-- PreTeXt's own.                                                  -->
    <!--                                                                 -->
    <!-- It depends on the name of a PreTeXt variable. If an upgrade     -->
    <!-- renames it, this line stops working without any error; the      -->
    <!-- re-check script in version-baseline.md looks for the name.      -->
    <!-- =============================================================== -->
    <xsl:variable name="b-needs-mono-font" select="true()"/>

</xsl:stylesheet>
